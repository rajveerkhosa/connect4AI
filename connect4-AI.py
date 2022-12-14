import numpy as np
import random
import pygame
import sys
import math

BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)

ROWS = 6
COLUMNS = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYERPIECE = 1
AIPIECE = 2

WINDOW_LENGTH = 4

def createBoard():
	board = np.zeros((ROWS,COLUMNS))
	return board

def dropPiece(board, row, col, piece):
	board[row][col] = piece

def isValidLocation(board, col):
	return board[ROWS-1][col] == 0

def nextOpenRow(board, col):
	for r in range(ROWS):
		if board[r][col] == 0:
			return r

def printBoard(board):
	print(np.flip(board, 0))

def winningMove(board, piece):
	# Check horizontal locations for win
	for c in range(COLUMNS-3):
		for r in range(ROWS):
			if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
				return True

	# Check vertical locations for win
	for c in range(COLUMNS):
		for r in range(ROWS-3):
			if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
				return True

	# Check positively sloped diaganols
	for c in range(COLUMNS-3):
		for r in range(ROWS-3):
			if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
				return True

	# Check negatively sloped diaganols
	for c in range(COLUMNS-3):
		for r in range(3, ROWS):
			if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
				return True

def evaluteWindow(window, piece):
	score = 0
	oppPiece = PLAYERPIECE
	if piece == PLAYERPIECE:
		oppPiece = AIPIECE

	if window.count(piece) == 4:
		score += 100
	elif window.count(piece) == 3 and window.count(EMPTY) == 1:
		score += 5
	elif window.count(piece) == 2 and window.count(EMPTY) == 2:
		score += 2

	if window.count(oppPiece) == 3 and window.count(EMPTY) == 1:
		score -= 4

	return score

def scorePosition(board, piece):
	score = 0

	## Score center column
	centerArray = [int(i) for i in list(board[:, COLUMNS//2])]
	centerCount = centerArray.count(piece)
	score += centerCount * 3

	## Score Horizontal
	for r in range(ROWS):
		rowArray = [int(i) for i in list(board[r,:])]
		for c in range(COLUMNS-3):
			window = rowArray[c:c+WINDOW_LENGTH]
			score += evaluteWindow(window, piece)

	## Score Vertical
	for c in range(COLUMNS):
		colArray = [int(i) for i in list(board[:,c])]
		for r in range(ROWS-3):
			window = colArray[r:r+WINDOW_LENGTH]
			score += evaluteWindow(window, piece)

	## Score posiive sloped diagonal
	for r in range(ROWS-3):
		for c in range(COLUMNS-3):
			window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluteWindow(window, piece)

	for r in range(ROWS-3):
		for c in range(COLUMNS-3):
			window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
			score += evaluteWindow(window, piece)

	return score

def isTerminalNode(board):
	return winningMove(board, PLAYERPIECE) or winningMove(board, AIPIECE) or len(getValidLocations(board)) == 0

def minimax(board, depth, alpha, beta, maximizingPlayer):
	validLocations = getValidLocations(board)
	isTerminal = isTerminalNode(board)
	if depth == 0 or isTerminal:
		if isTerminal:
			if winningMove(board, AIPIECE):
				return (None, 100000000000000)
			elif winningMove(board, PLAYERPIECE):
				return (None, -10000000000000)
			else: # Game is over, no more valid moves
				return (None, 0)
		else: # Depth is zero
			return (None, scorePosition(board, AIPIECE))
	if maximizingPlayer:
		value = -math.inf
		column = random.choice(validLocations)
		for col in validLocations:
			row = nextOpenRow(board, col)
			boardCopy = board.copy()
			dropPiece(boardCopy, row, col, AIPIECE)
			newScore = minimax(boardCopy, depth-1, alpha, beta, False)[1]
			if newScore > value:
				value = newScore
				column = col
			alpha = max(alpha, value)
			if alpha >= beta:
				break
		return column, value

	else: # Minimizing player
		value = math.inf
		column = random.choice(validLocations)
		for col in validLocations:
			row = nextOpenRow(board, col)
			boardCopy = board.copy()
			dropPiece(boardCopy, row, col, PLAYERPIECE)
			newScore = minimax(boardCopy, depth-1, alpha, beta, True)[1]
			if newScore < value:
				value = newScore
				column = col
			beta = min(beta, value)
			if alpha >= beta:
				break
		return column, value

def getValidLocations(board):
	validLocations = []
	for col in range(COLUMNS):
		if isValidLocation(board, col):
			validLocations.append(col)
	return validLocations

def bestMove(board, piece):

	validLocations = getValidLocations(board)
	bestScore = -10000
	bestColumn = random.choice(validLocations)
	for col in validLocations:
		row = nextOpenRow(board, col)
		temporaryBoard = board.copy()
		dropPiece(temporaryBoard, row, col, piece)
		score = scorePosition(temporaryBoard, piece)
		if score > bestScore:
			bestScore = score
			bestColumn = col

	return bestColumn

def draw_board(board):
	for c in range(COLUMNS):
		for r in range(ROWS):
			pygame.draw.rect(screen, BLUE, (c*squareSize, r*squareSize+squareSize, squareSize, squareSize))
			pygame.draw.circle(screen, BLACK, (int(c*squareSize+squareSize/2), int(r*squareSize+squareSize+squareSize/2)), RADIUS)
	
	for c in range(COLUMNS):
		for r in range(ROWS):		
			if board[r][c] == PLAYERPIECE:
				pygame.draw.circle(screen, RED, (int(c*squareSize+squareSize/2), height-int(r*squareSize+squareSize/2)), RADIUS)
			elif board[r][c] == AIPIECE: 
				pygame.draw.circle(screen, YELLOW, (int(c*squareSize+squareSize/2), height-int(r*squareSize+squareSize/2)), RADIUS)
	pygame.display.update()

board = createBoard()
printBoard(board)
gameOver = False

pygame.init()

squareSize = 100

width = COLUMNS * squareSize
height = (ROWS+1) * squareSize

size = (width, height)

RADIUS = int(squareSize/2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 75)

turn = random.randint(PLAYER, AI)

while not gameOver:

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.MOUSEMOTION:
			pygame.draw.rect(screen, BLACK, (0,0, width, squareSize))
			posx = event.pos[0]
			if turn == PLAYER:
				pygame.draw.circle(screen, RED, (posx, int(squareSize/2)), RADIUS)

		pygame.display.update()

		if event.type == pygame.MOUSEBUTTONDOWN:
			pygame.draw.rect(screen, BLACK, (0,0, width, squareSize))
			#print(event.pos)
			# Ask for Player 1 Input
			if turn == PLAYER:
				posx = event.pos[0]
				col = int(math.floor(posx/squareSize))

				if isValidLocation(board, col):
					row = nextOpenRow(board, col)
					dropPiece(board, row, col, PLAYERPIECE)

					if winningMove(board, PLAYERPIECE):
						label = myfont.render("Player 1 wins!!", 1, RED)
						screen.blit(label, (40,10))
						gameOver = True

					turn += 1
					turn = turn % 2

					printBoard(board)
					draw_board(board)


	# # Ask for Player 2 Input
	if turn == AI and not gameOver:				

		#col = random.randint(0, COLUMNS-1)
		#col = bestMove(board, AIPIECE)
		col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

		if isValidLocation(board, col):
			#pygame.time.wait(500)
			row = nextOpenRow(board, col)
			dropPiece(board, row, col, AIPIECE)

			if winningMove(board, AIPIECE):
				label = myfont.render("Player 2 wins!!", 1, YELLOW)
				screen.blit(label, (40,10))
				gameOver = True

			printBoard(board)
			draw_board(board)

			turn += 1
			turn = turn % 2

	if gameOver:
		pygame.time.wait(3000)