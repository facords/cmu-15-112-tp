# Helper function
# From: http://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#printing
def print2dList(a):
    if (a == []):
        print([])
        return
    rows = len(a)
    cols = len(a[0])
    fieldWidth = 2
    print("[", end="")
    for row in range(rows):
        if (row > 0): print("\n ", end="")
        print("[ ", end="")
        for col in range(cols):
            if (col > 0): print(" ", end="")
            formatSpec = "%" + str(fieldWidth) + "s"
            print(formatSpec % str(a[row][col]), end="")
        print(" ]", end="")
    print("]")

# -----------------------------------------------------------------------------
# Minimax algorithm

"""
gameState = current state of the game
alpha = best alternative for max on particular path through tree
beta  = best alternative for min on particular path through tree
"""

def minValue(gameState, alpha, beta):
    pass

def maxValue(gameState, alpha, beta):
    pass

class GameState(object):
    def __init__(self, boardSize):
        self.turn = 1
        self.gameOver = False
        self.board = list()
        self.boardSize = boardSize
    def getPlayerTurn(self, color=True):
        # Black player = 0
        # White player = 1
        if color: return "White" if self.turn % 2 == 1 else "Black "
        else: return self.turn % 2
    def resetBoard(self):
        self.turn = 1
        self.gameOver = False
        rng = range(self.boardSize)
        self.board = [["--" for c in rng] for r in rng]
    def updateBoard(self, piece, oldRowCol, newRowCol):
        rOld, cOld = oldRowCol
        rNew, cNew = newRowCol
        if rOld != None: self.board[rOld][cOld] = "--"
        if piece.active: self.board[rNew][cNew] = piece
        else: self.board[rNew][cNew] = "--"
    # def getAllPossibleMoves(self, player):

        # for row in self.boardSize:
        #     for col in self.boardSize:
        #         if self.board[row][col] != "--":
        #             self.board[row][col]
        
        # return possibleMoves
    def evaluate(self, pieces, blackKing):
        if self.gameOver:
            if blackKing.active: return -10000
            else: return 10000
        evalScore = 0
        for piece in pieces:
            if piece.active and (piece.pieceType != "king"):
                if piece.color == "white":
                    evalScore += piece.getCentipawns()
                else:
                    evalScore -= piece.getCentipawns()
        return evalScore




# class MinimaxAgent():
#     def __init__(self, maxDepth, playerColor):
#         self.maxDepth = maxDepth
#         self.playerColor = playerColor
#     def chooseMove(self, gameState):
#         # moves = 
#         # evalScore = self.miniMax(0, gameState, True)
#         # return move
#     def miniMax(self, currentDepth, gameState, isMaxTurn):
#         if (currentDepth == self.maxDepth) or (gameState.gameOver):
#             return gameState.evaluate()
#         for move in moves:
#             newGameState = 
#             node = self.miniMax(currentDepth+1, newGameState, not isMaxTurn)


