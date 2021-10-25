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


def drawCard(card: card_model.CardModel , ctx: cairo.Context):

    #Set background colour
    #ctx.set_source_rgb(0.3, 0.3, 1.0)
    #ctx.paint()

    ctx.select_font_face('serif')
    
    # Draw name
    ctx.set_font_size(layout.nameH)
    ctx.move_to(*layout.nameBL)
    ctx.show_text(card.nameStr)

    # Draw type
    ctx.set_font_size(layout.typeH)
    ctx.move_to(*layout.typeBL)
    ctx.show_text(card.typeStr)

    # Draw cardText
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
        ctx.set_font_size(layout.ptH)
        ctx.move_to(*layout.ptBL)
        ctx.show_text(ptStr)

    # Draw Mana Cost
    ctx.set_font_size(layout.nameH)
    ctx.move_to(
        layout.manaRight - ctx.text_extents(card.manaCost).width, 
        layout.nameBL[1]
    )
    ctx.show_text(card.manaCost)