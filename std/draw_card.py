import cairo
import std.card_model
import std.layout

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


def drawCard(card: std.card_model.CardModel , ctx: cairo.Context):

    #Set background colour
    #ctx.set_source_rgb(0.3, 0.3, 1.0)
    #ctx.paint()

    ctx.select_font_face('serif')
    
    # Draw name
    ctx.set_font_size(std.layout.nameH)
    ctx.move_to(*std.layout.nameBL)
    ctx.show_text(card.nameStr)

    # Draw type
    ctx.set_font_size(std.layout.typeH)
    ctx.move_to(*std.layout.typeBL)
    ctx.show_text(card.typeStr)

    # Draw cardText
    ctx.set_font_size(std.layout.cardTextH)
    showWrappedText(ctx, card.cardText,
        top=std.layout.cardTextBL[1], 
        left=std.layout.cardTextBL[0], 
        right=std.layout.cardTextBL[0] + std.layout.cardTextW,
        lineHeight=std.layout.cardTextH
    )

    # Draw power/toughness
    if card.power is not None:
        ptStr = str(card.power) + '/' + str(card.toughness)
        ctx.set_font_size(std.layout.ptH)
        ctx.move_to(*std.layout.ptBL)
        ctx.show_text(ptStr)

    # Draw Mana Cost
    ctx.set_font_size(std.layout.nameH)
    ctx.move_to(
        std.layout.manaRight - ctx.text_extents(card.manaCost).width, 
        std.layout.nameBL[1]
    )
    ctx.show_text(card.manaCost)
