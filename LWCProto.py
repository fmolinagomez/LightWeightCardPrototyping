#! /usr/bin/env python3
import argparse
import csv
import os
import pathlib
from typing import Iterable, List, Optional, Sequence, Tuple

import cairo
import numpy as np

import layout
from card_model import CardDeck, CardModel
from draw_card import drawCard
from utils import slugify


def extant_file(path: str) -> str:
    """Validate that a CLI argument points to an existing file."""
    if not os.path.exists(path):
        raise argparse.ArgumentTypeError(f"{path} does not exist")
    return path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deck Generator for Game Designers")
    parser.add_argument('-d', '--deck', type=extant_file, help='csv file containing the deck', metavar="FILE")
    parser.add_argument('-c', '--cards', type=extant_file, help='json file containing cards description', metavar="FILE", required=True)

    parser.add_argument('-i', '--images', help='Add images to cards', action='store_true')
    parser.add_argument('-r', '--rgb', help='Update layout card border colour with given R,G,B, only works with default layout', nargs=3, type=int)
    parser.add_argument('-l', '--layout', help='Use a different layout than default', type=extant_file, metavar="FILE")
    parser.add_argument('--single-card', help='Render each card as an individual 63x85mm PNG at 300 DPI', action='store_true')
    parser.add_argument('-o', '--output-dir', help='Directory where generated decks will be stored', default='decks')

    args = parser.parse_args()

    if args.single_card and args.deck is not None:
        parser.error('the --single-card option cannot be used together with --deck/-d')

    if (not args.single_card) and args.deck is None:
        parser.error('the --deck/-d option is required unless --single-card is specified')

    return args


def chunk_cards(cards: Sequence[CardModel], chunk_size: int = 9) -> Iterable[List[CardModel]]:
    for index in range(0, len(cards), chunk_size):
        yield list(cards[index:index + chunk_size])


def _require_image_helpers(*helpers) -> None:
    if any(helper is None for helper in helpers):
        raise RuntimeError(
            'Image helpers are not available. Make sure the --images flag '
            'is used when requesting image processing.'
        )


def build_card_list(
    *,
    cards: CardDeck,
    cards_file: str,
    deck_file: Optional[str],
    single_card_mode: bool,
) -> Tuple[str, List[CardModel], Optional[List[Sequence[str]]]]:
    card_db = cards.getDb()

    if single_card_mode:
        deck_name = pathlib.Path(cards_file).stem
        card_list: List[CardModel] = []
        for entry in card_db.values():
            card = CardModel()
            card.load(entry)
            card_list.append(card)
        return deck_name, card_list, None

    assert deck_file is not None
    deck_path = pathlib.Path(deck_file)
    deck_name = deck_path.stem
    card_list: List[CardModel] = []
    deck_rows: List[Sequence[str]] = []

    with deck_path.open(encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)

        try:
            header = next(reader)
        except StopIteration:
            return deck_name, card_list, deck_rows

        deck_rows.append(header)

        for row in reader:
            deck_rows.append(row)
            quantity = int(row[0])
            name = row[1]
            for _ in range(quantity):
                card_list.append(CardModel(name, card_db))

    return deck_name, card_list, deck_rows


def ensure_output_directories(
    base_dir: pathlib.Path,
    deck_name: str,
    single_card_mode: bool,
) -> Tuple[pathlib.Path, Optional[pathlib.Path]]:
    deck_dir = base_dir / deck_name
    deck_dir.mkdir(parents=True, exist_ok=True)

    cards_output_dir: Optional[pathlib.Path] = None
    if single_card_mode:
        cards_output_dir = deck_dir / 'cards'
        cards_output_dir.mkdir(parents=True, exist_ok=True)

    return deck_dir, cards_output_dir


def render_single_cards(
    card_list: Sequence[CardModel],
    *,
    deck_name: str,
    cards_output_dir: pathlib.Path,
    output_root: pathlib.Path,
    handle_images: bool,
    base_image_cls,
    add_image_fn,
    process_image_fn,
    load_full_frame_surface_fn,
) -> None:
    single_dpi = layout.SINGLE_CARD_DPI

    for index, card in enumerate(card_list):
        print(f'Card {index}: {card}')
        surf = layout.get_single_card_surface(single_dpi)
        ctx = cairo.Context(surf)

        card_matrix = layout.get_single_card_matrix(single_dpi)
        ctx.set_matrix(card_matrix)
        layout.clip_card(ctx)
        ctx.set_source_rgb(1, 1, 1)
        ctx.paint()

        if handle_images and card.imageFullFrame:
            _require_image_helpers(load_full_frame_surface_fn)
            full_frame_surface = load_full_frame_surface_fn(card, single_dpi)
            if full_frame_surface is not None:
                ctx.save()
                ctx.identity_matrix()
                ctx.set_source_surface(full_frame_surface, 0, 0)
                ctx.paint()
                ctx.restore()

        ctx.reset_clip()
        ctx.set_matrix(card_matrix)
        drawCard(card, ctx)

        card_filename = f"{index:03d}_{slugify(card.headerText)}.png"
        output_path = cards_output_dir / card_filename
        surf.write_to_png(str(output_path))

        if handle_images and not card.imageFullFrame:
            _require_image_helpers(
                base_image_cls,
                add_image_fn,
                process_image_fn,
            )
            process_image_fn(card, deck_name, dpi=single_dpi, output_root=output_root)
            base_image = base_image_cls(str(output_path))
            updated_image = add_image_fn(
                card,
                base_image,
                deck_name,
                dpi=single_dpi,
                output_root=output_root,
            )
            base_image.update(updated_image)
            base_image.save(str(output_path))


def _apply_layout_colour_modification(
    *,
    base_image,
    modify_layout: Sequence[int],
) -> None:
    from PIL import Image

    temp = base_image.baseImage.convert('RGBA')
    data = np.array(temp)
    red, green, blue, alpha = data.T
    for i in range(0, 63):
        white_areas = (red == 190 + i) & (blue == 190 + i) & (green == 190 + i)
        data[..., :-1][white_areas.T] = (
            modify_layout[0],
            modify_layout[1],
            modify_layout[2],
        )
    base_image.update(Image.fromarray(data))


def render_deck_pages(
    card_list: Sequence[CardModel],
    *,
    deck_name: str,
    deck_dir: pathlib.Path,
    output_root: pathlib.Path,
    handle_images: bool,
    modify_layout: Optional[Sequence[int]],
    base_image_cls,
    add_image_fn,
    process_image_fn,
    load_full_frame_surface_fn,
) -> None:
    for page_number, page in enumerate(chunk_cards(card_list)):
        print(f'Page {page_number}:')
        surf = layout.getSurface()
        ctx = cairo.Context(surf)

        page_dpi = layout.get_surface_dpi(surf)

        for index, card in enumerate(page):
            card_pos = (index % 3, index // 3)
            print(card_pos)
            print(card)

            if handle_images and card.imageFullFrame:
                _require_image_helpers(load_full_frame_surface_fn)
                full_frame_surface = load_full_frame_surface_fn(card, page_dpi)
                if full_frame_surface is not None:
                    card_origin_mm = layout.get_card_origin_mm(card_pos)
                    origin_px = layout.pair_mm_to_pixels(card_origin_mm, page_dpi)
                    ctx.save()
                    ctx.identity_matrix()
                    layout.clip_card_absolute(ctx, card_origin_mm, page_dpi)
                    ctx.set_source_surface(full_frame_surface, *origin_px)
                    ctx.paint()
                    ctx.restore()

            mat = layout.getMatrix(*card_pos, surf)
            ctx.set_matrix(mat)
            drawCard(card, ctx)

        output_path = deck_dir / f'{deck_name}_p{page_number}.png'
        surf.write_to_png(str(output_path))

        if modify_layout is not None:
            if base_image_cls is None:
                raise RuntimeError('Layout modifications require image helpers')
            base_image = base_image_cls(str(output_path))
            _apply_layout_colour_modification(
                base_image=base_image,
                modify_layout=modify_layout,
            )
            base_image.save(str(output_path))

        if handle_images:
            needs_partial_images = any(
                card.image is not None and not card.imageFullFrame for card in page
            )

            if needs_partial_images:
                _require_image_helpers(
                    base_image_cls,
                    add_image_fn,
                    process_image_fn,
                )
                base_image = base_image_cls(str(output_path))
                for index, card in enumerate(page):
                    if card.image is None or card.imageFullFrame:
                        continue

                    card_pos = (index % 3, index // 3)
                    card_origin_mm = layout.get_card_origin_mm(card_pos)
                    image_position_mm = (
                        card_origin_mm[0] + layout.ART_OFFSET_MM[0],
                        card_origin_mm[1] + layout.ART_OFFSET_MM[1],
                    )
                    process_image_fn(
                        card,
                        deck_name,
                        dpi=page_dpi,
                        output_root=output_root,
                    )
                    base_image.update(
                        add_image_fn(
                            card,
                            base_image,
                            deck_name,
                            position_mm=image_position_mm,
                            dpi=page_dpi,
                            output_root=output_root,
                        )
                    )

                base_image.save(str(output_path))


def write_deck_copy(
    deck_rows: Sequence[Sequence[str]],
    *,
    deck_name: str,
    deck_dir: pathlib.Path,
) -> None:
    deck_copy_path = deck_dir / f'{deck_name}.csv'
    with deck_copy_path.open('w', encoding='utf-8', newline='') as deck_copy:
        writer = csv.writer(deck_copy)
        for row in deck_rows:
            writer.writerow(row)


def main() -> None:
    args = parse_arguments()

    handle_images = args.images
    modify_layout = args.rgb
    cards_file = args.cards
    single_card_mode = args.single_card
    deck_file = args.deck
    output_root = pathlib.Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    cards = CardDeck(cards_file)
    deck_name, card_list, deck_rows = build_card_list(
        cards=cards,
        cards_file=cards_file,
        deck_file=deck_file,
        single_card_mode=single_card_mode,
    )

    deck_dir, cards_output_dir = ensure_output_directories(
        output_root,
        deck_name,
        single_card_mode,
    )

    base_image_cls = add_image_fn = process_image_fn = load_full_frame_surface_fn = None

    if handle_images or (modify_layout is not None):
        from add_images import BaseImage

        base_image_cls = BaseImage

    if handle_images:
        from add_images import addImage, load_full_frame_surface, processImage

        add_image_fn = addImage
        process_image_fn = processImage
        load_full_frame_surface_fn = load_full_frame_surface

    if single_card_mode and cards_output_dir is not None:
        render_single_cards(
            card_list,
            deck_name=deck_name,
            cards_output_dir=cards_output_dir,
            output_root=output_root,
            handle_images=handle_images,
            base_image_cls=base_image_cls,
            add_image_fn=add_image_fn,
            process_image_fn=process_image_fn,
            load_full_frame_surface_fn=load_full_frame_surface_fn,
        )
    else:
        render_deck_pages(
            card_list,
            deck_name=deck_name,
            deck_dir=deck_dir,
            output_root=output_root,
            handle_images=handle_images,
            modify_layout=modify_layout,
            base_image_cls=base_image_cls,
            add_image_fn=add_image_fn,
            process_image_fn=process_image_fn,
            load_full_frame_surface_fn=load_full_frame_surface_fn,
        )

    if (not single_card_mode) and deck_rows is not None:
        write_deck_copy(
            deck_rows,
            deck_name=deck_name,
            deck_dir=deck_dir,
        )


if __name__ == '__main__':
    main()
