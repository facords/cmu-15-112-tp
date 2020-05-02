# chess [ai]
# Developed by Florian Cords

import pygame
import random
import copy

BLACK          = (  0,   0,   0)
DARK_GRAY      = ( 18,  18,  18)
MEDIUM_GRAY    = ( 51,  51,  51)
LIGHT_GRAY     = (222, 222, 222)
HIGHLIGHT      = (255, 255,   0)
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
TITLE_Y       = 52
PMODE_X       = 160
PMODE_Y       = 60
RECT_MARGIN   = 18
LVLB_MARGIN   = 110
LVL_X         = 77
LVL_Y         = 40
LVL_W         = 185
LVL_H         = 59
BUTTON_W      = 310
BOX_X         = SCREEN_HEIGHT + BOX_WIDTH * 0.5
BOX_Y1        = SQUARE_DIM * 6.62
BOX_Y2        = SQUARE_DIM * 7.82
BOX_W         = 250
BOX_H         = 50
START_LETTER  = "a"
TITLE         = "chess [ai]"
LEVEL_ONE     = "level one"
LEVEL_TWO     = "level two"
LEVEL_THREE   = "level three"

# Centipawn values (standard chess point system)
PAWN   = 100
KNIGHT = 300
BISHOP = 300
ROOK   = 500
QUEEN  = 900
KING   = 0

pygame.init()
pygame.display.set_caption(TITLE)

screen        = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
labelFont     = pygame.font.SysFont("calibri", 14, bold=True)
titleFont1    = pygame.font.SysFont("corbel", 52)
titleFont2    = pygame.font.SysFont("corbel", 50)
buttonFont1   = pygame.font.SysFont("corbel", 40)
buttonFont2   = pygame.font.SysFont("calibri", 30)
textFont      = pygame.font.SysFont("corbel", 22, bold=True)
squares       = dict()
pieces        = list()
selectedPiece = None

# Chess piece images from: https://www.pngbarn.com/png-image-brxfd
wPawnImage   = pygame.image.load("whitePawn.png")
wKnightImage = pygame.image.load("whiteKnight.png")
wBishopImage = pygame.image.load("whiteBishop.png")
wRookImage   = pygame.image.load("whiteRook.png")
wQueenImage  = pygame.image.load("whiteQueen.png")
wKingImage   = pygame.image.load("whiteKing.png")
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
    pygame.draw.rect(screen, DARK_GRAY, box, 0)

def getSelectedSquare(x, y):
    for square in squares:
        if squares[square].collidepoint(x, y):
            selectedSquare = square
    return selectedSquare

def getOpponentColor(color):
    return ("black" if color == "white" else "white")

def toggleSquareColor(square, squareSelected):
    fillSquareColor(square, squareSelected)
    selectedPiece.movePiece(square)

def switchPlayer():
    clearMessage(3)
    player = gameState.getPlayerTurn()
    turn = textFont.render(f"turn: {player}", True, LIGHT_GRAY, DARK_GRAY)
    turnRect = turn.get_rect()
    turnRect.center = (BOX_X, SQUARE_DIM * 3)
    screen.blit(turn, turnRect)

def getOccupiedSquares(color="both", boardState=None):
    tempSet = set()
    if boardState == None:
        if color == "both":
            for piece in pieces:
                if piece.active:
                    tempSet.add(piece.location)
        else:
            for piece in pieces:
                if piece.active and (piece.color == color):
                    tempSet.add(piece.location)
    else:
        for row in range(BOARD_DIM):
            for col in range(BOARD_DIM):
                selection = boardState[row][col]
                if isinstance(selection, ChessPiece) and selection.active and \
                   (selection.color == color):
                    tempSet.add(selection.location)
    return tempSet

def getNonAttackPawnMoves(pawn):
    tempSet = set()
    row, col = getRowCol(pawn.location)
    dRow = -1 if pawn.color == "white" else 1
    occupiedSquares = getOccupiedSquares()
    tempSquare = getSquare(row+dRow, col)
    if (tempSquare in squares) and (tempSquare not in occupiedSquares):
        tempSet.add(tempSquare)
        if pawn.initialMove:
            tempSquare = getSquare(row+dRow*2, col)    
            if (tempSquare in squares) and (tempSquare not in occupiedSquares):
                tempSet.add(tempSquare)
    return tempSet

def getAttackPawnMoves(pawn):
    tempSet = set()
    row, col = getRowCol(pawn.location)
    dRow = -1 if pawn.color == "white" else 1
    for dCol in [-1, 1]:
        tempSquare = getSquare(row+dRow, col+dCol)
        if tempSquare in squares: tempSet.add(tempSquare)
    return tempSet

def getEnPassantPawn(row, col, color):
    otherPawn = None
    sameRow = 3 if color == "white" else 4
    if row == sameRow:
        tempList2 = [getSquare(sameRow, col-1), getSquare(sameRow, col+1)]
        for p in pieces:
            if p.active and (p.color != color) and (p.moveTurn == gameState.turn-1) and \
              (p.location in tempList2) and (p.moveCount == 1) and (p.pieceType == "pawn"):
                return p
    return otherPawn

def getLegalPawnMoves(selectedPiece, square, otherPiece=None):
    tempSet = getNonAttackPawnMoves(selectedPiece)
    color = selectedPiece.color
    row, col = getRowCol(square)
    dRow = -1 if color == "white" else 1
    # Regular attack moves
    if otherPiece != None:
        tempList1 = [getSquare(row+dRow, col-1), getSquare(row+dRow, col+1)]
        if otherPiece.location in tempList1: tempSet.add(otherPiece.location)
    # En passant attack moves
    otherPawn = getEnPassantPawn(row, col, color)
    if otherPawn != None:
        r, c = getRowCol(otherPawn.location)
        tempSet.add(getSquare(row+dRow, c))
    return tempSet

def getLegalKnightMoves(square):
    tempSet = set()
    row, col = getRowCol(square)
    for dRow in [-1, 1]:
        for dCol in [2, -2]:
            r, c = row + dRow, col + dCol
            tempSquare = getSquare(r, c)
            if (r in range(BOARD_DIM)) and (c in range(BOARD_DIM)):
                tempSet.add(tempSquare)
    for dRow in [2, -2]:
        for dCol in [1, -1]:
            r, c = row + dRow, col + dCol
            tempSquare = getSquare(r, c)
            if (r in range(BOARD_DIM)) and (c in range(BOARD_DIM)):
                tempSet.add(tempSquare)
    return tempSet

def getLegalBishopMoves(square):
    occupiedSquares = getOccupiedSquares()
    tempSet = set()
    row, col = getRowCol(square)
    dList = [-1, 1]
    for dRow in dList:
        for dCol in dList:
            r, c = row + dRow, col + dCol
            while (r in range(BOARD_DIM)) and (c in range(BOARD_DIM)):
                tempSquare = getSquare(r, c)
                if (tempSquare not in occupiedSquares):
                    tempSet.add(tempSquare)
                    r += dRow
                    c += dCol
                else:
                    tempSet.add(tempSquare)
                    break
    return tempSet

def getLegalRookMoves(square):
    occupiedSquares = getOccupiedSquares()
    tempSet = set()
    row, col = getRowCol(square)
    dList = [-1, 1]
    for d in dList:
        r = row + d
        while r in range(BOARD_DIM):
            tempSquare = getSquare(r, col)
            if tempSquare not in occupiedSquares:
                tempSet.add(tempSquare)
                r += d
            else:
                tempSet.add(tempSquare)
                break
    for d in dList:
        c = col + d
        while c in range(BOARD_DIM):
            tempSquare = getSquare(row, c)
            if tempSquare not in occupiedSquares:
                tempSet.add(tempSquare)
                c += d
            else:
                tempSet.add(tempSquare)
                break
    return tempSet

def getLegalQueenMoves(square):
    diagonalMoves = getLegalBishopMoves(square)
    cardinalMoves = getLegalRookMoves(square)
    return diagonalMoves.union(cardinalMoves)

def getSurroundingKingSquares(color):
    tempSet = set()
    king = whiteKing if color == "white" else blackKing
    row, col = getRowCol(king.location)
    dList = [-1, 0, 1]
    for dRow in dList:
        for dCol in dList:
            if not ((dRow == 0) and (dCol == 0)):
                tempSquare = getSquare(row+dRow, col+dCol)
                if tempSquare in squares: tempSet.add(tempSquare)
    return tempSet

def getLegalKingMoves(selectedPiece, square):
    tempSet = set()
    row, col = getRowCol(square)
    opponentColor = getOpponentColor(selectedPiece.color)
    surroundingKingSquares = getSurroundingKingSquares(opponentColor)
    selectedPiece.active = False
    opponentMoves = getAllLegalAttackMoves(opponentColor)
    selectedPiece.active = True
    restrictedMoves = opponentMoves.union(surroundingKingSquares)
    dList = [-1, 0, 1]
    for dRow in dList:
        for dCol in dList:
            if not ((dRow == 0) and (dCol == 0)):
                tempSquare = getSquare(row+dRow, col+dCol)
                if tempSquare in squares and tempSquare not in restrictedMoves:
                    tempSet.add(tempSquare)
    # Allow legal king-side and queen-side castling moves
    if (selectedPiece.location not in opponentMoves) and \
        selectedPiece.initialMove:
            occupiedSquares = getOccupiedSquares()
            illegalSquares = opponentMoves.union(occupiedSquares)
            if selectedPiece.color == "white":
                if whiteRook1.initialMove and whiteRook1.active and \
                    ("b1" not in occupiedSquares) and \
                    ("c1" not in illegalSquares) and \
                    ("d1" not in illegalSquares):
                        tempSet.add("c1")
                if whiteRook2.initialMove and whiteRook2.active and \
                    ("f1" not in illegalSquares) and \
                    ("g1" not in illegalSquares):
                        tempSet.add("g1")
            else:
                if blackRook1.initialMove and blackRook1.active and \
                    ("b8" not in occupiedSquares) and \
                    ("c8" not in illegalSquares) and \
                    ("d8" not in illegalSquares):
                        tempSet.add("c8")
                if blackRook2.initialMove and blackRook2.active and \
                    ("f8" not in illegalSquares) and \
                    ("g8" not in illegalSquares):
                        tempSet.add("g8")
    return tempSet

def getAllLegalAttackMoves(color, defending=False):
    tempSet = set()
    for piece in pieces:
        if piece.active and (piece.color == color):
            for square in piece.getLegalAttackMoves(False, defending):
                tempSet.add(square)
    return tempSet

def isKingInCheck(color):
    opponentMoves = getAllLegalAttackMoves(getOpponentColor(color))
    if color == "white":
        return (whiteKing.location in opponentMoves)
    else:
        return (blackKing.location in opponentMoves)

def getCheckThreatPieces(color):
    checkThreatPieces = list()
    tempList = list()
    for piece in pieces:
        if piece.active and (piece.color == getOpponentColor(color)):
            tempList.append(piece)
    for piece in tempList:
        piece.active = False
    for piece in tempList:
        piece.active = True
        if isKingInCheck(color): checkThreatPieces.append(piece)
        piece.active = False
    for piece in tempList:
        piece.active = True
    return checkThreatPieces

def canBlockCheck(king, attackingPiece):
    for piece in pieces:
        if piece.active and (piece.color == king.color) and \
            (piece.pieceType != "king"):
            currentSquare = piece.location
            for square in piece.getLegalAttackMoves(True):
                piece.location = square
                if not isKingInCheck(king.color):
                    piece.location = currentSquare
                    return True
            piece.location = currentSquare
    return False

def isCheckmate(color):
    king = whiteKing if color == "white" else blackKing
    kingMoves = king.getLegalAttackMoves()
    opponentColor = getOpponentColor(color)
    king.active = False
    attackMoves = getAllLegalAttackMoves(opponentColor)
    king.active = True
    surroundingKingSquares = getSurroundingKingSquares(opponentColor)
    opponentMoves = attackMoves.union(surroundingKingSquares)
    # Checkmate if king can't move out of check
    if kingMoves.issubset(opponentMoves):
        defensiveMoves = getAllLegalAttackMoves(color, True)
        checkThreatPieces = getCheckThreatPieces(color)
        if len(checkThreatPieces) > 1: return True
        else:
            # Checkmate if other pieces can't capture attacking piece
            if checkThreatPieces[0].location not in defensiveMoves:
                # Checkmate if other pieces can't block attack
                if not canBlockCheck(king, checkThreatPieces[0]):
                    return True
    return False

def isLegalMove(selectedPiece, selectedSquare, color, piece=None):
    # Can't move piece if move puts own king in check
    # or king is in check and move doesn't neutralize attack
    if selectedPiece.pieceType != "king":
        currentSquare = selectedPiece.location
        selectedPiece.location = selectedSquare
        if (piece != None) and (selectedSquare == piece.location):
            piece.active = False
        if isKingInCheck(color):
            selectedPiece.location = currentSquare
            if (piece != None): piece.active = True
            return False
        else:
            selectedPiece.location = currentSquare
            if (piece != None): piece.active = True
    # Compare move to legal moves
    if selectedPiece.pieceType == "pawn":
        if selectedSquare in getLegalPawnMoves(selectedPiece, selectedPiece.location, piece):
              return True
        else: return False
    elif selectedPiece.pieceType == "knight":
        if selectedSquare in getLegalKnightMoves(selectedPiece.location):
              return True
        else: return False
    elif selectedPiece.pieceType == "bishop":
        if selectedSquare in getLegalBishopMoves(selectedPiece.location):
              return True
        else: return False
    elif selectedPiece.pieceType == "rook":
        if selectedSquare in getLegalRookMoves(selectedPiece.location):
              return True
        else: return False
    elif selectedPiece.pieceType == "queen":
        if selectedSquare in getLegalQueenMoves(selectedPiece.location):
              return True
        else: return False
    elif selectedPiece.pieceType == "king":
        if selectedSquare in getLegalKingMoves(selectedPiece, selectedPiece.location):
              return True
        else: return False

def makeMove(selectedPiece, previousSquare, selectedSquare, opponentColor):
    clearMessage(4)
    fillSquareColor(previousSquare, False)
    selectedPiece.movePiece(selectedSquare)
    selectedPiece.moveCount += 1
    selectedPiece.moveTurn = gameState.turn
    if selectedPiece.initialMove: selectedPiece.initialMove = False
    gameState.turn += 1
    switchPlayer()
    if isKingInCheck(opponentColor):
        if isCheckmate(opponentColor):
            king = whiteKing if opponentColor == "white" else blackKing
            king.active = False
            message = f"checkmate! {selectedPiece.color} wins"
            gameState.gameOver = True
        else:
            gameState.gameOver = False
            message = f"{opponentColor} king in check!"
        showMessage(message)

def promotePawn(square, pieceColor):
    fillSquareColor(square, False)
    promotedQueen = ChessPiece(pieceColor, "queen")
    pieces.append(promotedQueen)
    promotedQueen.promoted = True
    promotedQueen.movePiece(square)

def killPiece(piece):
    square = piece.location
    fillSquareColor(square, False)
    piece.active = False

def getSelection(square, color="both"):
    if color == "both":
        for piece in pieces:
            if piece.active and (piece.location == square):
                return piece
    else:
        for piece in pieces:
            if piece.active and (piece.location == square) and \
              (piece.color == color):
                return piece
    return square

def getAllLegalMoves(color, boardState):
    allLegalMoves = list()
    allSquares = {s for s in squares}
    occupiedSquares = getOccupiedSquares(color, boardState)
    nonOccupiedSquares = allSquares.difference(occupiedSquares)
    opponentColor = getOpponentColor(color)
    boardStatePieces = list()
    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            selection = boardState[row][col]
            if isinstance(selection, ChessPiece):
                boardStatePieces.append(selection)
    for piece in boardStatePieces:
        if piece.active and (piece.color == color):
            for square in nonOccupiedSquares:
                selection = getSelection(square, opponentColor)
                if not isinstance(selection, ChessPiece): selection = None
                if isLegalMove(piece, square, color, selection):
                    allLegalMoves.append((piece, square))    
    return allLegalMoves

def evaluate(boardState):
    tempList = list()
    for row in range(BOARD_DIM):
        for col in range(BOARD_DIM):
            selection = boardState[row][col]
            if isinstance(selection, ChessPiece): tempList.append(selection)
    materialScore = 0
    for piece in tempList:
        if (piece.pieceType == "king") and (not piece.active):
            if piece.color == "black": return 10000
            else: return -10000
        elif piece.active and (piece.pieceType != "king"):
            if piece.color == "white":
                materialScore += piece.getCentipawns()
            else:
                materialScore -= piece.getCentipawns()
    return materialScore

def getNewBoardState(boardState, move):
    movingPiece = move[0]
    toSquare = move[1]
    movingPieceStartLocation = movingPiece.location
    rOld, cOld = getRowCol(movingPieceStartLocation)
    rNew, cNew = getRowCol(toSquare)
    selection = boardState[rNew][cNew]
    if isinstance(selection, ChessPiece): selection.active = False
    movingPiece.location = toSquare
    boardState[rOld][cOld] = "--"
    boardState[rNew][cNew] = movingPiece
    newBoardState = copy.deepcopy(boardState)
    if isinstance(selection, ChessPiece): selection.active = True
    movingPiece.location = movingPieceStartLocation
    boardState[rOld][cOld] = movingPiece
    boardState[rNew][cNew] = selection
    return newBoardState

def getPieceImage(color, pieceType):
    if color == "white":
        if   pieceType == "pawn":   return wPawnImage
        elif pieceType == "knight": return wKnightImage
        elif pieceType == "bishop": return wBishopImage
        elif pieceType == "rook":   return wRookImage
        elif pieceType == "queen":  return wQueenImage
        elif pieceType == "king":   return wKingImage
    else:
        if   pieceType == "pawn":   return bPawnImage
        elif pieceType == "knight": return bKnightImage
        elif pieceType == "bishop": return bBishopImage
        elif pieceType == "rook":   return bRookImage
        elif pieceType == "queen":  return bQueenImage
        elif pieceType == "king":   return bKingImage

class ChessPiece(object):
    def __init__(self, color, pieceType):
        self.color = color
        self.pieceType = pieceType
        self.location = "Off_Board"
        self.initialMove = True
        self.moveCount = 0
        self.moveTurn = 0
        self.active = True
        self.promoted = False
    def __repr__(self):
        if self.pieceType == "king":
            return f"{self.pieceType[0]}{self.color[0]}".upper()
        else:
            return f"{self.color[0]}{self.pieceType[0]}".upper()
    def __eq__(self, other):
        return (isinstance(other, ChessPiece) and \
                (self.color     == other.color) and \
                (self.pieceType == other.pieceType) and \
                (self.active    == other.active == True) and \
                (self.location  == other.location))
    def getCentipawns(self):
        if   self.pieceType == "pawn":   return PAWN
        elif self.pieceType == "knight": return KNIGHT
        elif self.pieceType == "bishop": return BISHOP
        elif self.pieceType == "rook":   return ROOK
        elif self.pieceType == "queen":  return QUEEN
        elif self.pieceType == "king":   return KING
    def movePiece(self, newSquare):
        if (self.pieceType == "king") and (self.location != "Off_Board") and self.initialMove:
            # King-side and queen-side castling moves!
            if newSquare == "c1":
                whiteRook1.movePiece("d1")
                fillSquareColor("a1", False)
            elif newSquare == "g1":
                whiteRook2.movePiece("f1")
                fillSquareColor("h1", False)
            elif newSquare == "c8":
                blackRook1.movePiece("d8")
                fillSquareColor("a8", False)
            elif newSquare == "g8":
                blackRook2.movePiece("f8")
                fillSquareColor("h8", False)
        if self.location != "Off_Board":
            oldRow, oldCol = getRowCol(self.location)
        else:
            oldRow = oldCol = None
        newRow, newCol = getRowCol(newSquare)
        gameState.updateBoard(self, (oldRow, oldCol), (newRow, newCol))
        self.location = newSquare
        image = getPieceImage(self.color, self.pieceType)
        screen.blit(image, (squares[newSquare][0], squares[newSquare][1]))
        if self.pieceType == "pawn":
            # Pawn promotion
            if (((self.color == "white") and (self.location[1] == "8")) or \
                ((self.color == "black") and (self.location[1] == "1"))):
                    self.active = False
                    promotePawn(self.location, self.color)
            # Pawn en passant attack
            otherPawn = getEnPassantPawn(oldRow, oldCol, self.color)
            if (otherPawn != None):
                r, c = getRowCol(otherPawn.location)
                dRow = -1 if self.color == "white" else 1
                if newSquare == getSquare(r+dRow, c): killPiece(otherPawn)
    def getLegalAttackMoves(self, nonAttackingPawn=False, defending=False):
        if self.pieceType == "pawn":
            if nonAttackingPawn: return getNonAttackPawnMoves(self)
            else: return getAttackPawnMoves(self)
        elif self.pieceType == "knight":
            return getLegalKnightMoves(self.location)
        elif self.pieceType == "bishop":
            return getLegalBishopMoves(self.location)
        elif self.pieceType == "rook":
            return getLegalRookMoves(self.location)
        elif self.pieceType == "queen":
            return getLegalQueenMoves(self.location)
        elif self.pieceType == "king":
            tempSet = set()
            friendlySquares = getOccupiedSquares(self.color)
            if defending:
                opponentColor = getOpponentColor(self.color)
                self.active = False
                opponentMoves = getAllLegalAttackMoves(opponentColor)
                self.active = True
            row, col = getRowCol(self.location)
            dList = [-1, 0, 1]
            for dRow in dList:
                for dCol in dList:
                    if not ((dRow == 0) and (dCol == 0)):
                        tempSquare = getSquare(row+dRow, col+dCol)
                        if (tempSquare in squares) and \
                           (tempSquare not in friendlySquares):
                            tempSet.add(tempSquare)
                            if defending and (tempSquare in opponentMoves):
                                tempSet.remove(tempSquare)
            return tempSet

# Algorithm inspired by: https://towardsdatascience.com/create-ai-for-your-own-board-game-from-scratch-minimax-part-2-517e1c1e3362
class GameState(object):
    def __init__(self):
        self.turn = 1
        self.gameOver = False
        self.board = list()
    def getPlayerTurn(self, color=True):
        # Black player = 0
        # White player = 1
        if color: return "white" if self.turn % 2 == 1 else "black"
        else: return self.turn % 2
    def resetBoard(self):
        self.turn = 1
        self.gameOver = False
        rng = range(BOARD_DIM)
        self.board = [["--" for c in rng] for r in rng]
    def updateBoard(self, piece, oldRowCol, newRowCol, board=None):
        b = self.board if board == None else board
        rOld, cOld = oldRowCol
        rNew, cNew = newRowCol
        if rOld != None: b[rOld][cOld] = "--"
        if piece.active: b[rNew][cNew] = piece
        else: board[rNew][cNew] = "--"
        if board != None: return b

# Algorithm inspired by: https://towardsdatascience.com/create-ai-for-your-own-board-game-from-scratch-minimax-part-2-517e1c1e3362
class MinimaxAgent():
    def __init__(self, maxDepth, color):
        self.maxDepth = maxDepth
        self.color = color
    def chooseMove(self, boardState):
        alpha = float("-inf")
        beta  = float("inf")
        evalScore, selectedMove = self.minimaxAlphaBeta(0, boardState, True, alpha, beta)
        return selectedMove
    def isGameOver(self, boardState):
        if len(getAllLegalMoves("white", boardState)) == 0: return True
        if len(getAllLegalMoves("black", boardState)) == 0: return True
        return False
    def minimaxAlphaBeta(self, currentDepth, boardState, isMinTurn, alpha, beta):
        if (currentDepth == self.maxDepth) or self.isGameOver(boardState):
            return evaluate(boardState), ""
        color = "black" if isMinTurn else "white"
        allLegalMoves = getAllLegalMoves(color, boardState)
        random.shuffle(allLegalMoves)
        bestEval = float("inf") if isMinTurn else float("-inf")
        bestMove = ""
        for move in allLegalMoves:
            newState = getNewBoardState(boardState, move)
            childEval, childMove = self.minimaxAlphaBeta(currentDepth+1, newState, not isMinTurn, alpha, beta)
            if isMinTurn and (childEval < bestEval):
                bestMove = move
                bestEval = childEval
                beta = min(beta, bestEval)
                if beta <= alpha: break
            if (not isMinTurn) and (childEval > bestEval):
                bestMove = move
                bestEval = childEval
                alpha = max(alpha, bestEval)
                if beta <= alpha: break
        return bestEval, bestMove

# Initialize white chess pieces
whitePawn1   = ChessPiece("white", "pawn")
whitePawn2   = ChessPiece("white", "pawn")
whitePawn3   = ChessPiece("white", "pawn")
whitePawn4   = ChessPiece("white", "pawn")
whitePawn5   = ChessPiece("white", "pawn")
whitePawn6   = ChessPiece("white", "pawn")
whitePawn7   = ChessPiece("white", "pawn")
whitePawn8   = ChessPiece("white", "pawn")
whiteKnight1 = ChessPiece("white", "knight")
whiteKnight2 = ChessPiece("white", "knight")
whiteBishop1 = ChessPiece("white", "bishop")
whiteBishop2 = ChessPiece("white", "bishop")
whiteRook1   = ChessPiece("white", "rook")
whiteRook2   = ChessPiece("white", "rook")
whiteQueen   = ChessPiece("white", "queen")
whiteKing    = ChessPiece("white", "king")

# Initialize black chess pieces
blackPawn1   = ChessPiece("black", "pawn")
blackPawn2   = ChessPiece("black", "pawn")
blackPawn3   = ChessPiece("black", "pawn")
blackPawn4   = ChessPiece("black", "pawn")
blackPawn5   = ChessPiece("black", "pawn")
blackPawn6   = ChessPiece("black", "pawn")
blackPawn7   = ChessPiece("black", "pawn")
blackPawn8   = ChessPiece("black", "pawn")
blackKnight1 = ChessPiece("black", "knight")
blackKnight2 = ChessPiece("black", "knight")
blackBishop1 = ChessPiece("black", "bishop")
blackBishop2 = ChessPiece("black", "bishop")
blackRook1   = ChessPiece("black", "rook")
blackRook2   = ChessPiece("black", "rook")
blackQueen   = ChessPiece("black", "queen")
blackKing    = ChessPiece("black", "king")

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
    gameState.resetBoard()
    whitePawn1.movePiece("a2")
    whitePawn2.movePiece("b2")
    whitePawn3.movePiece("c2")
    whitePawn4.movePiece("d2")
    whitePawn5.movePiece("e2")
    whitePawn6.movePiece("f2")
    whitePawn7.movePiece("g2")
    whitePawn8.movePiece("h2")
    whiteKnight1.movePiece("b1")
    whiteKnight2.movePiece("g1")
    whiteBishop1.movePiece("c1")
    whiteBishop2.movePiece("f1")
    whiteRook1.movePiece("a1")
    whiteRook2.movePiece("h1")
    whiteQueen.movePiece("d1")
    whiteKing.movePiece("e1")
    blackPawn1.movePiece("a7")
    blackPawn2.movePiece("b7")
    blackPawn3.movePiece("c7")
    blackPawn4.movePiece("d7")
    blackPawn5.movePiece("e7")
    blackPawn6.movePiece("f7")
    blackPawn7.movePiece("g7")
    blackPawn8.movePiece("h7")
    blackKnight1.movePiece("b8")
    blackKnight2.movePiece("g8")
    blackBishop1.movePiece("c8")
    blackBishop2.movePiece("f8")
    blackRook1.movePiece("a8")
    blackRook2.movePiece("h8")
    blackQueen.movePiece("d8")
    blackKing.movePiece("e8")

def start(level=None):
    screen.fill(MEDIUM_GRAY)
    drawBox()
    drawBoard()
    drawBoardLabels()
    setChessBoard()
    initializeBoxText(level)

def reset():
    drawBoard()
    resetChessPieces()
    setChessBoard()
    switchPlayer()
    clearMessage(4)

def resetChessPieces():
    index = 0
    while index < len(pieces):
        if pieces[index].promoted:
            pieces.remove(pieces[index])
        else:
            pieces[index].location = "Off_Board"
            pieces[index].moveCount = 0
            pieces[index].initialMove = True
            pieces[index].active = True
            index += 1

def blitText(font, text, y):
    text = font.render(text, True, LIGHT_GRAY)
    textRect = text.get_rect()
    textRect.center = (BOX_X, y)
    screen.blit(text, textRect)

def initializeBoxText(level):
    blitText(titleFont2, TITLE, SQUARE_DIM)
    playerMode = f"one player: {level}" if onePlayerMode else "two player"
    blitText(textFont, playerMode, SQUARE_DIM*2)
    switchPlayer()
    clearMessage(4)

def showMessage(message):
    clearMessage(4)
    if gameState.gameOver: clearMessage(3)
    m = textFont.render(message, True, LIGHT_GRAY, DARK_GRAY)
    mRect = m.get_rect()
    mRect.center = (BOX_X, SQUARE_DIM*4)
    screen.blit(m, mRect)

def clearMessage(level):
    rect = pygame.Rect(LVL_X, LVL_Y, BUTTON_W, LVL_H)
    rect.center = (BOX_X, SQUARE_DIM*level)
    pygame.draw.rect(screen, DARK_GRAY, rect, 0)

def showMainScreen(onePlayerRect, twoPlayerRect):
    # Chess photo by Felix Mittermeier on Unsplash (https://unsplash.com)
    # Image also found here: https://towardsdatascience.com/create-ai-for-your-own-board-game-from-scratch-minimax-part-2-517e1c1e3362
    mainScreenImage = pygame.image.load("mainScreen.jpg")
    screen.blit(mainScreenImage, (0, 0))
    title = titleFont1.render(TITLE, True, LIGHT_GRAY)
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

def showLevelButtons(lvl1, lvl1Rect, lvl2, lvl2Rect, lvl3, lvl3Rect):
    r1 = r2 = r3 = pygame.Rect(LVL_X, LVL_Y, LVL_W, LVL_H)
    r1.center = (PMODE_X, PMODE_Y+1*LVLB_MARGIN)
    pygame.draw.rect(screen, BLACK, r1, 0)
    pygame.draw.rect(screen, LIGHT_GRAY, r1, 2)
    lvl1Rect.center = (PMODE_X, PMODE_Y+1*LVLB_MARGIN)
    lvl1Rect.width = LVL_W
    lvl1Rect.height = LVL_H
    screen.blit(lvl1, lvl1Rect)
    if r1.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, HIGHLIGHT, r1, 2)
        lvl1 = buttonFont2.render(LEVEL_ONE, True, HIGHLIGHT, BLACK)
        screen.blit(lvl1, lvl1Rect)
    r2.center = (PMODE_X, PMODE_Y+2*LVLB_MARGIN)
    pygame.draw.rect(screen, BLACK, r2, 0)
    pygame.draw.rect(screen, LIGHT_GRAY, r2, 2)
    lvl2Rect.center = (PMODE_X, PMODE_Y+2*LVLB_MARGIN)
    lvl2Rect.width = LVL_W
    lvl2Rect.height = LVL_H
    screen.blit(lvl2, lvl2Rect)
    if r2.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, HIGHLIGHT, r2, 2)
        lvl2 = buttonFont2.render(LEVEL_TWO, True, HIGHLIGHT, BLACK)
        screen.blit(lvl2, lvl2Rect)
    r3.center = (PMODE_X, PMODE_Y+3*LVLB_MARGIN)
    pygame.draw.rect(screen, BLACK, r3, 0)
    pygame.draw.rect(screen, LIGHT_GRAY, r3, 2)
    lvl3Rect.center = (PMODE_X, PMODE_Y+3*LVLB_MARGIN)
    lvl3Rect.width = LVL_W
    lvl3Rect.height = LVL_H
    screen.blit(lvl3, lvl3Rect)
    if r3.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(screen, HIGHLIGHT, r3, 2)
        lvl3 = buttonFont2.render(LEVEL_THREE, True, HIGHLIGHT, BLACK)
        screen.blit(lvl3, lvl3Rect)

def showRestartReturnButtons(restartRect, returnRect):
    resLabel = textFont.render("restart game", True, LIGHT_GRAY, DARK_GRAY)
    resRect = resLabel.get_rect()
    resRect.center = restartRect.center
    screen.blit(resLabel, resRect)
    pygame.draw.rect(screen, LIGHT_GRAY, restartRect, 2)
    if restartRect.collidepoint(pygame.mouse.get_pos()):
        resLabel = textFont.render("restart game", True, HIGHLIGHT, DARK_GRAY)
        screen.blit(resLabel, resRect)
        pygame.draw.rect(screen, HIGHLIGHT, restartRect, 2)
    retLabel = textFont.render("return to main screen", True, LIGHT_GRAY, DARK_GRAY)
    retRect = retLabel.get_rect()
    retRect.center = returnRect.center
    screen.blit(retLabel, retRect)
    pygame.draw.rect(screen, LIGHT_GRAY, returnRect, 2)
    if returnRect.collidepoint(pygame.mouse.get_pos()):
        retLabel = textFont.render("return to main screen", True, HIGHLIGHT, DARK_GRAY)
        screen.blit(retLabel, retRect)
        pygame.draw.rect(screen, HIGHLIGHT, returnRect, 2)

gameState     = GameState()
onMainScreen  = True
onePlayerMode = True
showLevels    = False
playing       = True

onePlayerButtonColor = twoPlayerButtonColor = LIGHT_GRAY

while playing: 

    restartRect = pygame.Rect(LVL_X, LVL_Y, BOX_W, BOX_H)
    returnRect  = pygame.Rect(LVL_X, LVL_Y, BOX_W, BOX_H)

    if onMainScreen:
        onePlayer = buttonFont1.render("one player", True, onePlayerButtonColor)
        twoPlayer = buttonFont1.render("two player", True, twoPlayerButtonColor)
        onePlayerRect = onePlayer.get_rect()
        twoPlayerRect = twoPlayer.get_rect()
        lvl1 = buttonFont2.render(LEVEL_ONE, True, LIGHT_GRAY)
        lvl2 = buttonFont2.render(LEVEL_TWO, True, LIGHT_GRAY)
        lvl3 = buttonFont2.render(LEVEL_THREE, True, LIGHT_GRAY)
        lvl1Rect = lvl1.get_rect()
        lvl2Rect = lvl2.get_rect()
        lvl3Rect = lvl3.get_rect()
        showMainScreen(onePlayerRect, twoPlayerRect)
        if showLevels: showLevelButtons(lvl1, lvl1Rect, lvl2, lvl2Rect, lvl3, lvl3Rect)
    else:
        restartRect.center = (BOX_X, BOX_Y1)
        returnRect.center = (BOX_X, BOX_Y2)
        showRestartReturnButtons(restartRect, returnRect)
        playerTurn = gameState.getPlayerTurn()
        numberOfMoves = len(getAllLegalMoves(playerTurn, gameState.board))
        activePieces = list()
        for piece in pieces:
            if piece.active and (piece.pieceType != "king"):
                activePieces.append(piece)
        if ((not gameState.gameOver) and (numberOfMoves == 0)) or (len(activePieces) == 0):
                gameState.gameOver = True
                showMessage("the game is a draw!")
        # Minimax Alpha-Beta agent move
        if onePlayerMode and (not gameState.gameOver) and (playerTurn == "black"):
            selectedMove = minimaxAgent.chooseMove(gameState.board)
            movingPiece = selectedMove[0]
            toSquare = selectedMove[1]
            selection = getSelection(toSquare, "white")
            if isinstance(selection, ChessPiece): killPiece(selection)
            makeMove(movingPiece, movingPiece.location, toSquare, "white")

    # Event loop
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            playing = False

        if onMainScreen and (event.type == pygame.MOUSEBUTTONDOWN) and \
            onePlayerRect.collidepoint(pygame.mouse.get_pos()):
                onePlayerButtonColor = HIGHLIGHT
        else: onePlayerButtonColor = LIGHT_GRAY

        if onMainScreen and (event.type == pygame.MOUSEBUTTONDOWN) and \
            twoPlayerRect.collidepoint(pygame.mouse.get_pos()):
                twoPlayerButtonColor = HIGHLIGHT
        else: twoPlayerButtonColor = LIGHT_GRAY

        if onMainScreen and (event.type == pygame.MOUSEBUTTONUP):
            if onePlayerRect.collidepoint(pygame.mouse.get_pos()):
                if showLevels: showLevels = False
                else: showLevels = True
            elif lvl1Rect.collidepoint(pygame.mouse.get_pos()):
                onePlayerMode = True
                onMainScreen  = False
                minimaxAgent  = MinimaxAgent(1, "black")
                start(LEVEL_ONE)
            elif lvl2Rect.collidepoint(pygame.mouse.get_pos()):
                onePlayerMode = True
                onMainScreen  = False
                minimaxAgent  = MinimaxAgent(2, "black")
                start(LEVEL_TWO)
            elif lvl3Rect.collidepoint(pygame.mouse.get_pos()):
                onePlayerMode = True
                onMainScreen  = False
                minimaxAgent  = MinimaxAgent(3, "black")
                start(LEVEL_THREE)
            elif twoPlayerRect.collidepoint(pygame.mouse.get_pos()):
                showLevels    = False
                onePlayerMode = False
                onMainScreen  = False
                start()
            else:
                showLevels = False

        if (not onMainScreen) and (event.type == pygame.MOUSEBUTTONUP):
            if restartRect.collidepoint(pygame.mouse.get_pos()):
                selectedPiece = None
                reset()
            elif returnRect.collidepoint(pygame.mouse.get_pos()):
                selectedPiece = None
                resetChessPieces()
                showLevels = False
                onMainScreen = True

        if (not onMainScreen) and (event.type == pygame.MOUSEBUTTONDOWN):

            x, y = pygame.mouse.get_pos()

            if (not gameState.gameOver) and \
               (x >= BOARDER) and (x <= BOARDER + BOARD_DIM*SQUARE_DIM) and \
               (y >= BOARDER) and (y <= BOARDER + BOARD_DIM*SQUARE_DIM):

                # Identify selected chess piece or selected square name
                selectedSquare = getSelectedSquare(x, y)
                selection = getSelection(selectedSquare)

                if (selectedPiece == None) and \
                   isinstance(selection, ChessPiece) and \
                   (selection.color == playerTurn):
                        selectedPiece = selection
                        toggleSquareColor(selectedSquare, True)

                elif (selectedPiece != None) and \
                    isinstance(selection, ChessPiece):

                    previousSquare = selectedPiece.location
                    toggleSquareColor(previousSquare, False)

                    if selection.color != selectedPiece.color:
                        if isLegalMove(selectedPiece, selectedSquare, selectedPiece.color, selection):
                            # Capture opponent's chess piece
                            killPiece(selection)
                            makeMove(selectedPiece, previousSquare, selection.location, selection.color)
                            selectedPiece = None
                        else:
                            toggleSquareColor(previousSquare, True)
                    else:
                        if previousSquare == selectedSquare:
                            toggleSquareColor(selectedSquare, False)
                            selectedPiece = None
                        else:
                            selectedPiece = selection
                            toggleSquareColor(selectedSquare, True)

                elif selectedPiece != None:
                    if isLegalMove(selectedPiece, selectedSquare, selectedPiece.color):
                        previousSquare = selectedPiece.location
                        opponentColor = getOpponentColor(selectedPiece.color)
                        makeMove(selectedPiece, previousSquare, selectedSquare, opponentColor)
                        selectedPiece = None

    pygame.display.update()

pygame.quit()