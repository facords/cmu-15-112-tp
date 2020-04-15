# chess [ai]
# Developed by Florian Cords

import pygame

pygame.init()
pygame.display.set_caption("chess [ai]")

BLACK          = (  0,   0,   0)
DARK_GRAY      = ( 51,  51,  51)
LIGHT_GRAY     = (222, 222, 222)
YELLOW         = (255, 255,   0)
TAN            = (255, 252, 237)
GREEN          = ( 79, 121,  66)
SELECTED_TAN   = (233, 225, 185)
SELECTED_GREEN = (124, 175, 114)

BOARDER       = 25
BOARD_DIM     = 8
SQUARE_DIM    = 70
BOX_WIDTH     = 350
SCREEN_HEIGHT = 2 * BOARDER + BOARD_DIM * SQUARE_DIM
SCREEN_WIDTH  = SCREEN_HEIGHT + BOX_WIDTH
START_LETTER  = "a"
IMAGE_HEIGHT  = 196
TITLE_Y       = 52
PMODE_X       = 160
PMODE_Y       = 60
RECT_MARGIN   = 18

screen        = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
labelFont     = pygame.font.SysFont("calibri", 14, bold=True)
titleFont     = pygame.font.SysFont("corbel", 52)
buttonFont    = pygame.font.SysFont("corbel", 40)
trackerFont   = pygame.font.SysFont("corbel", 30)
squares       = dict()
pieces        = list()
selectedPiece = None

# Load white chess piece images
wPawnImage   = pygame.image.load("whitePawn.png")
wKnightImage = pygame.image.load("whiteKnight.png")
wBishopImage = pygame.image.load("whiteBishop.png")
wRookImage   = pygame.image.load("whiteRook.png")
wQueenImage  = pygame.image.load("whiteQueen.png")
wKingImage   = pygame.image.load("whiteKing.png")

# Load black chess piece images
bPawnImage   = pygame.image.load("blackPawn.png")
bKnightImage = pygame.image.load("blackKnight.png")
bBishopImage = pygame.image.load("blackBishop.png")
bRookImage   = pygame.image.load("blackRook.png")
bQueenImage  = pygame.image.load("blackQueen.png")
bKingImage   = pygame.image.load("blackKing.png")

def getTopLeft(row, col):
    x = BOARDER + col * SQUARE_DIM
    y = BOARDER + row * SQUARE_DIM
    return (x, y)

# View to Model
def getRowCol(square):
    row = BOARD_DIM - int(square[1])
    col = ord(square[0]) - ord(START_LETTER)
    return row, col

# Model to View
def getSquare(row, col):
    return chr(ord(START_LETTER)+col) + str(BOARD_DIM-row)

def fillSquareColor(square, selected):
    row, col = getRowCol(square)
    sqRect = squares[square]
    if selected:
        if ((row % 2 == 0) and (col % 2 == 0)) or \
           ((row % 2 == 1) and (col % 2 == 1)):
            pygame.draw.rect(screen, SELECTED_TAN, sqRect, 0)
        else:
            pygame.draw.rect(screen, SELECTED_GREEN, sqRect, 0)
    else:
        if ((row % 2 == 0) and (col % 2 == 0)) or \
           ((row % 2 == 1) and (col % 2 == 1)):
            pygame.draw.rect(screen, TAN, sqRect, 0)
        else:
            pygame.draw.rect(screen, GREEN, sqRect, 0)

def drawBoard():
    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            square = getSquare(row, col)
            sqRect = pygame.Rect(getTopLeft(row, col), (SQUARE_DIM, SQUARE_DIM))
            squares[square] = sqRect
            fillSquareColor(square, False)

def redrawBoard():
    for square in squares:
        fillSquareColor(square, False)

def drawBoardLabels():
    startLetter = START_LETTER.upper()
    for i in range(BOARD_DIM):
        letter = labelFont.render(chr(ord(startLetter)+i), True, LIGHT_GRAY)
        number = labelFont.render(str(1+i), True, LIGHT_GRAY)
        letterRect = letter.get_rect()
        numberRect = number.get_rect()
        x = BOARDER + SQUARE_DIM * (0.5 + i)
        y = BOARDER * 1.5 + BOARD_DIM * SQUARE_DIM
        letterRect.center = (x, y)
        x = BOARDER * 0.5
        y = BOARDER + SQUARE_DIM * (BOARD_DIM - 0.5 - i)
        numberRect.center = (x, y)
        screen.blit(letter, letterRect)
        screen.blit(number, numberRect)

def drawBox():
    x = 2 * BOARDER + BOARD_DIM * SQUARE_DIM
    y = 0
    w = SCREEN_WIDTH - x
    h = SCREEN_HEIGHT
    box = pygame.Rect((x, y), (w, h))
    pygame.draw.rect(screen, BLACK, box, 0)

def getSelectedSquare(x, y):
    for square in squares:
        if squares[square].collidepoint(x, y):
            selectedSquare = square
    return selectedSquare

def getOpponentColor(color):
    return ("black" if color == "white" else "white")

def toggleSquareColor(square, squareSelected):
    fillSquareColor(square, squareSelected)
    selectedPiece.MovePiece(square)

def switchPlayer(previousPlayer):
    # TO BUILD: Toggle players (black player can't select white pieces)
    player = "Black " if previousPlayer == "white" else "White"
    turn = trackerFont.render(f"Turn: {player}", True, LIGHT_GRAY, BLACK)
    turnRect = turn.get_rect()
    x = SCREEN_HEIGHT + BOX_WIDTH * 0.5
    y = SQUARE_DIM
    turnRect.center = (x, y)
    screen.blit(turn, turnRect)

def isSquareOccupied(square):
    for piece in pieces:
        if piece.active and (piece.location == square):
            return True
    return False

def getOccupiedSquares(color=""):
    tempSet = set()
    if color == "":
        for piece in pieces:
            if piece.active:
                tempSet.add(piece.location)
    else:
        for piece in pieces:
            if piece.active and (piece.color == color):
                tempSet.add(piece.location)
    return tempSet

def getLegalPawnMoves(square, otherPiece=None):
    tempList = list()
    row, col = getRowCol(square)
    if selectedPiece.color == "white":
        if not isSquareOccupied(getSquare(row-1, col)):
            tempList.append(getSquare(row-1, col))
            if selectedPiece.initialMove and \
                (not isSquareOccupied(getSquare(row-2, col))):
                tempList.append(getSquare(row-2, col))
        if otherPiece != None:
            if (otherPiece.location == getSquare(row-1, col-1)) or \
               (otherPiece.location == getSquare(row-1, col+1)):
                tempList.append(otherPiece.location)
        # TO BUILD: En passant moves
        # - The capturing pawn must be on its fifth rank
        # - The opponent pawn must move two squares, landing directly alongside
        #   the capturing pawn on the fifth rank
        # - You must make the capture immediately; you only get one chance to
        #   capture en passant

        # Allow en passant moves
        # if ...
    else:
        if not isSquareOccupied(getSquare(row+1, col)):
            tempList.append(getSquare(row+1, col))
            if selectedPiece.initialMove and \
                (not isSquareOccupied(getSquare(row+2, col))):
                tempList.append(getSquare(row+2, col))
        if otherPiece != None:
            if (otherPiece.location == getSquare(row+1, col-1)) or \
               (otherPiece.location == getSquare(row+1, col+1)):
                tempList.append(otherPiece.location)
        # Allow en passant moves
        # if ...
    return tempList

def getLegalKnightMoves(square):
    tempList = list()
    row, col = getRowCol(square)
    if (row-2 in range(BOARD_DIM)) and (col-1 in range(BOARD_DIM)):
        tempList.append(getSquare(row-2, col-1))
    if (row-2 in range(BOARD_DIM)) and (col+1 in range(BOARD_DIM)):
        tempList.append(getSquare(row-2, col+1))
    if (row+2 in range(BOARD_DIM)) and (col-1 in range(BOARD_DIM)):
        tempList.append(getSquare(row+2, col-1))
    if (row+2 in range(BOARD_DIM)) and (col+1 in range(BOARD_DIM)):
        tempList.append(getSquare(row+2, col+1))
    if (row-1 in range(BOARD_DIM)) and (col-2 in range(BOARD_DIM)):
        tempList.append(getSquare(row-1, col-2))
    if (row+1 in range(BOARD_DIM)) and (col-2 in range(BOARD_DIM)):
        tempList.append(getSquare(row+1, col-2))
    if (row-1 in range(BOARD_DIM)) and (col+2 in range(BOARD_DIM)):
        tempList.append(getSquare(row-1, col+2))
    if (row+1 in range(BOARD_DIM)) and (col+2 in range(BOARD_DIM)):
        tempList.append(getSquare(row+1, col+2))
    return tempList

def getLegalBishopMoves(square, otherPiece=None):
    tempList = list()
    row, col = getRowCol(square)
    dList = [1, -1]
    for dRow in dList:
        for dCol in dList:
            r, c = row + dRow, col + dCol
            while (r in range(BOARD_DIM)) and (c in range(BOARD_DIM)):
                tempSquare = getSquare(r, c)
                if (not isSquareOccupied(tempSquare)) or \
                   (otherPiece != None and \
                    otherPiece.location == tempSquare):
                    tempList.append(tempSquare)
                    r += dRow
                    c += dCol
                else:
                    tempList.append(tempSquare)
                    break
    return tempList

def getLegalRookMoves(square, otherPiece=None):
    tempList = list()
    row, col = getRowCol(square)
    dList = [1, -1]
    for d in dList:
        r = row + d
        while r in range(BOARD_DIM):
            tempSquare = getSquare(r, col)
            if (not isSquareOccupied(tempSquare)) or \
               (otherPiece != None and \
                otherPiece.location == tempSquare):
                tempList.append(tempSquare)
                r += d
            else:
                tempList.append(tempSquare)
                break
    for d in dList:
        c = col + d
        while c in range(BOARD_DIM):
            tempSquare = getSquare(row, c)
            if (not isSquareOccupied(tempSquare)) or \
               (otherPiece != None and \
                otherPiece.location == tempSquare):
                tempList.append(tempSquare)
                c += d
            else:
                tempList.append(tempSquare)
                break
    return tempList

def getLegalQueenMoves(square, otherPiece=None):
    diagonalMoves = getLegalBishopMoves(square, otherPiece)
    cardinalMoves = getLegalRookMoves(square, otherPiece)
    return diagonalMoves + cardinalMoves

def getLegalKingMoves(square, piece=None):
    tempList = list()
    row, col = getRowCol(square)
    if piece != None:
        decisionPiece = piece
    else:
        decisionPiece = selectedPiece
    # King can't move or capture into check
    opponentColor = getOpponentColor(decisionPiece.color)
    opponentMoves = getAllLegalAttackMoves(opponentColor)
    if getSquare(row+1, col) not in opponentMoves:
        tempList.append(getSquare(row+1, col))
    if getSquare(row-1, col) not in opponentMoves:
        tempList.append(getSquare(row-1, col))
    if getSquare(row, col+1) not in opponentMoves:
        tempList.append(getSquare(row, col+1))
    if getSquare(row, col-1) not in opponentMoves:
        tempList.append(getSquare(row, col-1))
    if getSquare(row+1, col+1) not in opponentMoves:
        tempList.append(getSquare(row+1, col+1))
    if getSquare(row-1, col-1) not in opponentMoves:
        tempList.append(getSquare(row-1, col-1))
    if getSquare(row-1, col+1) not in opponentMoves:
        tempList.append(getSquare(row-1, col+1))
    if getSquare(row+1, col-1) not in opponentMoves:
        tempList.append(getSquare(row+1, col-1))
    # Allow legal king-side and queen-side castling moves
    if decisionPiece.location not in opponentMoves:
        if decisionPiece.initialMove:
            occupiedSquares = getOccupiedSquares()
            opponentSquares = opponentMoves.union(occupiedSquares)
            if decisionPiece.color == "white":
                if whiteRook1.initialMove and whiteRook1.active and \
                    ("b1" not in occupiedSquares) and \
                    ("c1" not in opponentSquares) and \
                    ("d1" not in opponentSquares):
                    tempList.append(getSquare(row, col-2))
                if whiteRook2.initialMove and whiteRook2.active and \
                    ("f1" not in opponentSquares) and \
                    ("g1" not in opponentSquares):
                    tempList.append(getSquare(row, col+2))
            else:
                if blackRook1.initialMove and blackRook1.active and \
                    ("b8" not in occupiedSquares) and \
                    ("c8" not in opponentSquares) and \
                    ("d8" not in opponentSquares):
                    tempList.append(getSquare(row, col-2))
                if blackRook2.initialMove and blackRook2.active and \
                    ("f8" not in opponentSquares) and \
                    ("g8" not in opponentSquares):
                    tempList.append(getSquare(row, col+2))
    return tempList

def getAllLegalAttackMoves(color):
    tempSet = set()
    for piece in pieces:
        if piece.active and (piece.color == color):
            for square in piece.GetLegalAttackMoves(selectedPiece):
                tempSet.add(square)
    return tempSet

def isKingInCheck(color):
    opponentMoves = getAllLegalAttackMoves(getOpponentColor(color))
    if color == "white":
        return (whiteKing.location in opponentMoves)
    else:
        return (blackKing.location in opponentMoves)

def isCheckmate(color):
    return False
    # TO BUILD:
    #   Checkmate only if:
    #       = King can't move out of check (done)
    #       - Other pieces can't block threat (not done)

    # opponentMoves = getAllLegalAttackMoves(getOpponentColor(color))
    # if color == "white":
    #     whiteKingSquares = set(whiteKing.GetLegalAttackMoves())
    #     return whiteKingSquares.issubset(opponentMoves)
    # else:
    #     blackKingSquares = set(blackKing.GetLegalAttackMoves())
    #     return blackKingSquares.issubset(opponentMoves)

def isLegalMove(selectedSquare, piece=None):
    # TO BUILD:
    #   - Can't move piece if it puts own king in check
    #   - Can't move piece if king is in check and move doesn't block threat
    if selectedPiece.pieceType == "pawn":
        if selectedSquare in getLegalPawnMoves(selectedPiece.location, piece):
              return True
        else: return False
    elif selectedPiece.pieceType == "knight":
        if selectedSquare in getLegalKnightMoves(selectedPiece.location):
              return True
        else: return False
    elif selectedPiece.pieceType == "bishop":
        if selectedSquare in getLegalBishopMoves(selectedPiece.location, piece):
              return True
        else: return False
    elif selectedPiece.pieceType == "rook":
        if selectedSquare in getLegalRookMoves(selectedPiece.location, piece):
              return True
        else: return False
    elif selectedPiece.pieceType == "queen":
        if selectedSquare in getLegalQueenMoves(selectedPiece.location, piece):
              return True
        else: return False
    elif selectedPiece.pieceType == "king":
        if selectedSquare in getLegalKingMoves(selectedPiece.location):
              return True
        else: return False

def makeMove(selectedPiece, previousSquare, selectedSquare, opponentColor):
    fillSquareColor(previousSquare, False)
    selectedPiece.MovePiece(selectedSquare)
    selectedPiece.initialMove = False
    switchPlayer(selectedPiece.color)
    selectedPiece = None
    # POSSIBLY BUILD: evaluateCheckAndCheckmate() function
    if isKingInCheck(opponentColor):
        if isCheckmate(opponentColor):
            winner = getOpponentColor(opponentColor).title()
            print(f"Checkmate! {winner} wins.")
        else:
            print(f"{opponentColor.title()} king in check!")

def promotePawn(square, pieceColor):
    # POSSIBLY BUILD: Option to promote to other pieces via dialog box
    fillSquareColor(square, False)
    if pieceColor == "white": image = wQueenImage
    else: image = bQueenImage
    promotedQueen = ChessPiece(pieceColor, "queen", image)
    pieces.append(promotedQueen)
    promotedQueen.promoted = True
    promotedQueen.MovePiece(square)

class ChessPiece(object):
    def __init__(self, color, pieceType, image):
        self.color = color.strip().lower()
        self.pieceType = pieceType.strip().lower()
        self.image = image
        self.location = "Off_Board"
        self.initialMove = True
        self.active = True
        self.promoted = False
    def __repr__(self):
        return f"{self.color}-{self.pieceType}-{self.location}"
    def __eq__(self, other):
        return (isinstance(other, ChessPiece) and \
                (self.color     == other.color) and \
                (self.pieceType == other.pieceType) and \
                (self.active    == other.active == True) and \
                (self.location  == other.location))
    def MovePiece(self, newSquare):
        if (self.pieceType == "king") and (self.location != "Off_Board") and \
            self.initialMove:
            # King-side and queen-side castling moves!
            if newSquare == "c1":
                whiteRook1.MovePiece("d1")
                fillSquareColor("a1", False)
            elif newSquare == "g1":
                whiteRook2.MovePiece("f1")
                fillSquareColor("h1", False)
            elif newSquare == "c8":
                blackRook1.MovePiece("d8")
                fillSquareColor("a8", False)
            elif newSquare == "g8":
                blackRook2.MovePiece("f8")
                fillSquareColor("h8", False)
        self.location = newSquare
        screen.blit(self.image, (squares[newSquare][0], squares[newSquare][1]))
        if (self.pieceType == "pawn") and \
            (((self.color == "white") and (self.location[1] == "8")) or \
             ((self.color == "black") and (self.location[1] == "1"))):
            # Pawn promotion!
            self.active = False
            promotePawn(self.location, self.color)
    def GetLegalAttackMoves(self, attackedPiece=None):
        if self.pieceType == "pawn":
            # TO FIX: Don't add squares outside of board
            tempList = list()
            row, col = getRowCol(self.location)
            dRow = -1 if self.color == "white" else 1
            tempList.append(getSquare(row+dRow, col-1))
            tempList.append(getSquare(row+dRow, col+1))
            return tempList
        elif self.pieceType == "knight":
            return getLegalKnightMoves(self.location)
        elif self.pieceType == "bishop":
            return getLegalBishopMoves(self.location, attackedPiece)
        elif self.pieceType == "rook":
            return getLegalRookMoves(self.location, attackedPiece)
        elif self.pieceType == "queen":
            return getLegalQueenMoves(self.location, attackedPiece)
        elif self.pieceType == "king":
            tempList = list()
            row, col = getRowCol(self.location)
            dList = [-1, 0, 1]
            for dRow in dList:
                for dCol in dList:
                    if (dRow != 0) and (dCol != 0):
                        tempSquare = getSquare(row+dRow, col+dCol)
                        if (tempSquare in squares) and \
                           (tempSquare not in getOccupiedSquares(self.color)):
                            tempList.append(tempSquare)
            return tempList

"""
Minimax algorithm notes:
state = current state of the game
alpha = best alternative for max on particular path through tree
beta  = best alternative for min on particular path through tree
"""

def minValue(state, alpha, beta):
    pass

def maxValue(state, alpha, beta):
    pass

# Initialize white chess pieces
whitePawn1   = ChessPiece("white", "pawn", wPawnImage)
whitePawn2   = ChessPiece("white", "pawn", wPawnImage)
whitePawn3   = ChessPiece("white", "pawn", wPawnImage)
whitePawn4   = ChessPiece("white", "pawn", wPawnImage)
whitePawn5   = ChessPiece("white", "pawn", wPawnImage)
whitePawn6   = ChessPiece("white", "pawn", wPawnImage)
whitePawn7   = ChessPiece("white", "pawn", wPawnImage)
whitePawn8   = ChessPiece("white", "pawn", wPawnImage)
whiteKnight1 = ChessPiece("white", "knight", wKnightImage)
whiteKnight2 = ChessPiece("white", "knight", wKnightImage)
whiteBishop1 = ChessPiece("white", "bishop", wBishopImage)
whiteBishop2 = ChessPiece("white", "bishop", wBishopImage)
whiteRook1   = ChessPiece("white", "rook", wRookImage)
whiteRook2   = ChessPiece("white", "rook", wRookImage)
whiteQueen   = ChessPiece("white", "queen", wQueenImage)
whiteKing    = ChessPiece("white", "king", wKingImage)

# Initialize black chess pieces
blackPawn1   = ChessPiece("black", "pawn", bPawnImage)
blackPawn2   = ChessPiece("black", "pawn", bPawnImage)
blackPawn3   = ChessPiece("black", "pawn", bPawnImage)
blackPawn4   = ChessPiece("black", "pawn", bPawnImage)
blackPawn5   = ChessPiece("black", "pawn", bPawnImage)
blackPawn6   = ChessPiece("black", "pawn", bPawnImage)
blackPawn7   = ChessPiece("black", "pawn", bPawnImage)
blackPawn8   = ChessPiece("black", "pawn", bPawnImage)
blackKnight1 = ChessPiece("black", "knight", bKnightImage)
blackKnight2 = ChessPiece("black", "knight", bKnightImage)
blackBishop1 = ChessPiece("black", "bishop", bBishopImage)
blackBishop2 = ChessPiece("black", "bishop", bBishopImage)
blackRook1   = ChessPiece("black", "rook", bRookImage)
blackRook2   = ChessPiece("black", "rook", bRookImage)
blackQueen   = ChessPiece("black", "queen", bQueenImage)
blackKing    = ChessPiece("black", "king", bKingImage)

# Add all chess pieces to pieces list
pieces.append(whitePawn1)
pieces.append(whitePawn2)
pieces.append(whitePawn3)
pieces.append(whitePawn4)
pieces.append(whitePawn5)
pieces.append(whitePawn6)
pieces.append(whitePawn7)
pieces.append(whitePawn8)
pieces.append(whiteKnight1)
pieces.append(whiteKnight2)
pieces.append(whiteBishop1)
pieces.append(whiteBishop2)
pieces.append(whiteRook1)
pieces.append(whiteRook2)
pieces.append(whiteQueen)
pieces.append(whiteKing)
pieces.append(blackPawn1)
pieces.append(blackPawn2)
pieces.append(blackPawn3)
pieces.append(blackPawn4)
pieces.append(blackPawn5)
pieces.append(blackPawn6)
pieces.append(blackPawn7)
pieces.append(blackPawn8)
pieces.append(blackKnight1)
pieces.append(blackKnight2)
pieces.append(blackBishop1)
pieces.append(blackBishop2)
pieces.append(blackRook1)
pieces.append(blackRook2)
pieces.append(blackQueen)
pieces.append(blackKing)

# Set or reset the chess board
def setChessBoard():
    whitePawn1.MovePiece("a2")
    whitePawn2.MovePiece("b2")
    whitePawn3.MovePiece("c2")
    whitePawn4.MovePiece("d2")
    whitePawn5.MovePiece("e2")
    whitePawn6.MovePiece("f2")
    whitePawn7.MovePiece("g2")
    whitePawn8.MovePiece("h2")
    whiteKnight1.MovePiece("b1")
    whiteKnight2.MovePiece("g1")
    whiteBishop1.MovePiece("c1")
    whiteBishop2.MovePiece("f1")
    whiteRook1.MovePiece("a1")
    whiteRook2.MovePiece("h1")
    whiteQueen.MovePiece("d1")
    whiteKing.MovePiece("e1")
    blackPawn1.MovePiece("a7")
    blackPawn2.MovePiece("b7")
    blackPawn3.MovePiece("c7")
    blackPawn4.MovePiece("d7")
    blackPawn5.MovePiece("e7")
    blackPawn6.MovePiece("f7")
    blackPawn7.MovePiece("g7")
    blackPawn8.MovePiece("h7")
    blackKnight1.MovePiece("b8")
    blackKnight2.MovePiece("g8")
    blackBishop1.MovePiece("c8")
    blackBishop2.MovePiece("f8")
    blackRook1.MovePiece("a8")
    blackRook2.MovePiece("h8")
    blackQueen.MovePiece("d8")
    blackKing.MovePiece("e8")

def resetChessPieces():
    for piece in pieces:
        piece.location = "Off_Board"
        if piece.promoted:
            piece.initialMove = False
            piece.active = False
        else:
            piece.initialMove = True
            piece.active = True

def start():
    screen.fill(DARK_GRAY)
    drawBox()
    drawBoard()
    drawBoardLabels()
    setChessBoard()
    setStartingTurnTracker()
    backgroundImage = pygame.image.load("gameOver.png")
    screen.blit(backgroundImage, (SCREEN_HEIGHT, SCREEN_HEIGHT-IMAGE_HEIGHT))

def setStartingTurnTracker():
    turn = trackerFont.render("Turn: White", True, LIGHT_GRAY, BLACK)
    turnRect = turn.get_rect()
    x = SCREEN_HEIGHT + BOX_WIDTH * 0.5
    y = SQUARE_DIM
    turnRect.center = (x, y)
    screen.blit(turn, turnRect)

def showMainScreen(onePlayerRect, twoPlayerRect):
    mainScreenImage = pygame.image.load("mainScreen.png")
    screen.blit(mainScreenImage, (0, 0))

    title = titleFont.render("chess [ai]", True, LIGHT_GRAY)
    titleRect = title.get_rect()
    titleRect.center = (SCREEN_WIDTH * 0.5, TITLE_Y)
    screen.blit(title, titleRect)

    onePlayerRect.center = (PMODE_X, PMODE_Y)
    screen.blit(onePlayer, onePlayerRect)

    twoPlayerRect.center = (SCREEN_WIDTH - PMODE_X, PMODE_Y)
    screen.blit(twoPlayer, twoPlayerRect)

    if onePlayerRect.collidepoint(pygame.mouse.get_pos()):
        onePlayerHoverRect = onePlayerRect
        onePlayerHoverRect.width  = onePlayerRect.width  + RECT_MARGIN
        onePlayerHoverRect.height = onePlayerRect.height + RECT_MARGIN
        onePlayerHoverRect.center = (PMODE_X, PMODE_Y)
        pygame.draw.rect(screen, onePlayerButtonColor, onePlayerHoverRect, 2)

    if twoPlayerRect.collidepoint(pygame.mouse.get_pos()):
        twoPlayerHoverRect = twoPlayerRect
        twoPlayerHoverRect.width  = twoPlayerRect.width  + RECT_MARGIN
        twoPlayerHoverRect.height = twoPlayerRect.height + RECT_MARGIN
        twoPlayerHoverRect.center = (SCREEN_WIDTH - PMODE_X, PMODE_Y)
        pygame.draw.rect(screen, twoPlayerButtonColor, twoPlayerHoverRect, 2)

onMainScreen = True
playing = True
onePlayerButtonColor = twoPlayerButtonColor = LIGHT_GRAY

while playing:

    if onMainScreen:
        onePlayer = buttonFont.render("one player", True, onePlayerButtonColor)
        twoPlayer = buttonFont.render("two player", True, twoPlayerButtonColor)
        onePlayerRect = onePlayer.get_rect()
        twoPlayerRect = twoPlayer.get_rect()
        showMainScreen(onePlayerRect, twoPlayerRect)

    # Event loop
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            playing = False

        if onMainScreen and (event.type == pygame.MOUSEBUTTONDOWN) and \
            onePlayerRect.collidepoint(pygame.mouse.get_pos()):
                onePlayerButtonColor = YELLOW
        else: onePlayerButtonColor = LIGHT_GRAY

        if onMainScreen and (event.type == pygame.MOUSEBUTTONDOWN) and \
            twoPlayerRect.collidepoint(pygame.mouse.get_pos()):
                twoPlayerButtonColor = YELLOW
        else: twoPlayerButtonColor = LIGHT_GRAY

        if onMainScreen and (event.type == pygame.MOUSEBUTTONUP):
            if onePlayerRect.collidepoint(pygame.mouse.get_pos()):
                pass
            elif twoPlayerRect.collidepoint(pygame.mouse.get_pos()):
                onMainScreen = False
                start()
        
        if (not onMainScreen) and (event.type == pygame.KEYDOWN):
            if event.key == pygame.K_r:
                setStartingTurnTracker()
                redrawBoard()
                resetChessPieces()
                setChessBoard()
            elif event.key == pygame.K_h:
                setStartingTurnTracker()
                redrawBoard()
                resetChessPieces()
                setChessBoard()
                onMainScreen = True
        
        if (not onMainScreen) and (event.type == pygame.MOUSEBUTTONDOWN):

            # TO BUILD: Toggle players (black player can't select white pieces)

            x, y = pygame.mouse.get_pos()
            if (x >= BOARDER) and (x <= BOARDER + BOARD_DIM*SQUARE_DIM) and \
               (y >= BOARDER) and (y <= BOARDER + BOARD_DIM*SQUARE_DIM):

                selectedSquare = getSelectedSquare(x, y)

                # Identify selected chess piece or selected square name
                for piece in pieces:
                    if piece.active and piece.location == selectedSquare:
                        selection = piece
                        break
                    else:
                        selection = selectedSquare

                # Select, unselect, move, and capture chess pieces
                if selectedPiece == None and isinstance(selection, ChessPiece):
                    selectedPiece = selection
                    toggleSquareColor(selectedSquare, True)

                elif isinstance(selection, ChessPiece):

                    previousSquare = selectedPiece.location
                    toggleSquareColor(previousSquare, False)

                    if selection.color != selectedPiece.color:
                        if isLegalMove(selectedSquare, selection):
                            # Capture opponent's chess piece
                            square = selection.location
                            fillSquareColor(square, False)
                            selection.active = False
                            print(f"Captured: {selection}")
                            makeMove(selectedPiece, previousSquare,
                                     square, selection.color)
                            selectedPiece = None
                        else:
                            selectedPiece = selection
                            toggleSquareColor(selectedSquare, True)
                    else:
                        if previousSquare == selectedSquare:
                            toggleSquareColor(selectedSquare, False)
                            selectedPiece = None
                        else:
                            selectedPiece = selection
                            toggleSquareColor(selectedSquare, True)

                elif selectedPiece != None:
                    if isLegalMove(selectedSquare):
                        previousSquare = selectedPiece.location
                        opponentColor = getOpponentColor(selectedPiece.color)
                        makeMove(selectedPiece, previousSquare,
                                 selectedSquare, opponentColor)
                        selectedPiece = None

    pygame.display.update()

pygame.quit()