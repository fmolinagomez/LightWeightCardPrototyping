import cairo
import card_model
import layout

def showWrappedText(
    ctx: cairo.Context,
    text: str,
    top=0.0,
    left=0.0,
    right=None,
    lineHeight=12.0
):
    maxWidth = right - left
    inputLines = text.split('\n')
    inputWords = [line.split(' ') for line in inputLines]
    
    currentOffset = 0

    for line in inputWords:
        currentLine = []

        while len(line):
            nextWord = line.pop(0)
            nextLine = currentLine + [nextWord]

            if (ctx.text_extents(' '.join(nextLine)).width > maxWidth):
                ctx.move_to(left, top + currentOffset)
                ctx.show_text(' '.join(currentLine))
                currentLine = [nextWord]
                currentOffset = currentOffset + lineHeight
            else:
                currentLine = nextLine
        
        if (len(currentLine)):
            ctx.move_to(left, top + currentOffset)
            ctx.show_text(' '.join(currentLine))
            currentOffset = currentOffset + lineHeight * 1.4


def drawCard(
    card: card_model.CardModel,
    ctx: cairo.Context,
):

    ctx.save()
    layout.clip_card(ctx)

    if not card.imageFullFrame:
        ctx.set_source_rgb(*card.get_background_color_rgb())
        ctx.paint()


    ctx.select_font_face('serif')

    header_color = card.get_header_text_color_rgb()
    body_color = card.get_text_color_rgb()

    ctx.set_font_size(layout.nameH)

    if card.headerBanner:
        header_text = card.headerText or ''
        text_extents = ctx.text_extents(header_text)
        padding = 1.0
        banner_top = layout.nameBL[1] + text_extents.y_bearing - padding
        banner_height = text_extents.height + padding * 2
        if banner_height <= 0:
            banner_height = layout.nameH + padding * 2
        banner_top = max(banner_top, 0.0)

        ctx.save()
        ctx.set_source_rgb(*card.get_header_banner_color_rgb())
        ctx.rectangle(0, banner_top, layout.CARD_WIDTH_MM, banner_height)
        ctx.fill()
        ctx.restore()

    # Draw header text
    ctx.set_source_rgb(*header_color)
    ctx.move_to(*layout.nameBL)
    ctx.show_text(card.headerText)

    # Draw type
    ctx.set_source_rgb(*body_color)
    ctx.set_font_size(layout.typeH)
    ctx.move_to(*layout.typeBL)
    ctx.show_text(card.typeStr)

    # Draw cardText
    ctx.set_source_rgb(*body_color)
    ctx.set_font_size(layout.cardTextH)
    showWrappedText(ctx, card.cardText,
        top=layout.cardTextBL[1],
        left=layout.cardTextBL[0],
        right=layout.cardTextBL[0] + layout.cardTextW,
        lineHeight=layout.cardTextH
    )

    # Draw power/toughness
    if card.power is not None:
        ptStr = str(card.power) + '/' + str(card.toughness)
        ctx.set_source_rgb(*body_color)
        ctx.set_font_size(layout.ptH)
        ctx.move_to(*layout.ptBL)
        ctx.show_text(ptStr)

    # Draw command points shield
    ctx.save()
    shield_x, shield_y = layout.commandPointsShieldTL
    shield_width, shield_height = layout.commandPointsShieldSize
    point_height = layout.commandPointsShieldPointHeight

    ctx.move_to(shield_x, shield_y)
    ctx.line_to(shield_x + shield_width, shield_y)
    ctx.line_to(shield_x + shield_width, shield_y + shield_height * 0.65)
    ctx.line_to(shield_x + shield_width / 2.0, shield_y + shield_height + point_height)
    ctx.line_to(shield_x, shield_y + shield_height * 0.65)
    ctx.close_path()

    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.fill_preserve()
    ctx.set_line_width(layout.commandPointsBorderWidth)
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.stroke()

    ctx.set_font_size(layout.commandPointsFontSize)
    text = str(card.commandPoints)
    extents = ctx.text_extents(text)
    center_x = shield_x + shield_width / 2.0
    center_y = shield_y + (shield_height + point_height) / 2.0
    text_x = center_x - (extents.x_bearing + extents.width / 2.0)
    text_y = center_y - (extents.y_bearing + extents.height / 2.0)

    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.move_to(text_x, text_y)
    ctx.show_text(text)
    ctx.restore()

    # Draw footer text
    if card.footerText:
        footer_slant = cairo.FONT_SLANT_NORMAL
        footer_weight = cairo.FONT_WEIGHT_NORMAL

        if card.footerFontStyle == 'italic':
            footer_slant = cairo.FONT_SLANT_ITALIC
        if card.footerFontStyle == 'bold':
            footer_weight = cairo.FONT_WEIGHT_BOLD

        ctx.set_source_rgb(*card.get_footer_text_color_rgb())
        ctx.set_font_size(layout.footerH)
        ctx.select_font_face('serif', footer_slant, footer_weight)
        ctx.move_to(*layout.footerBL)
        ctx.show_text(card.footerText)
        ctx.select_font_face('serif')

    # Draw footer text
    if card.footerText:
        footer_slant = cairo.FONT_SLANT_NORMAL
        footer_weight = cairo.FONT_WEIGHT_NORMAL

        if card.footerFontStyle == 'italic':
            footer_slant = cairo.FONT_SLANT_ITALIC
        if card.footerFontStyle == 'bold':
            footer_weight = cairo.FONT_WEIGHT_BOLD

        ctx.set_source_rgb(*card.get_footer_text_color_rgb())
        ctx.set_font_size(layout.footerH)
        ctx.select_font_face('serif', footer_slant, footer_weight)
        ctx.move_to(*layout.footerBL)
        ctx.show_text(card.footerText)
        ctx.select_font_face('serif')


    ctx.restore()

