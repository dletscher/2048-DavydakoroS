from Game2048 import *

class Player(BasePlayer):
	def __init__(self, timeLimit):
		BasePlayer.__init__(self, timeLimit)

		self._nodeCount = 0
		self._parentCount = 0
		self._childCount = 0
		self._depthCount = 0
		self._count = 0

	def findMove(self, state):
		self._count += 1
		actions = self.moveOrder(state)
		depth = 1
		while self.timeRemaining():
			self._depthCount += 1
			self._parentCount += 1
			self._nodeCount += 1
			print('Search depth', depth)
			best = -10000
			alpha = -1000000
			beta = 1000000
			for a in actions:
				result = state.move(a)
				if not self.timeRemaining(): return
				v = self.minPlayer(result, depth-1, alpha, beta)
				if v is None: return
				if v > best:
					best = v
					bestMove = a
				if best >= beta:
					break
				if best > alpha:
					alpha = best
						
			self.setMove(bestMove)
			print('\tBest value', best, bestMove)

			depth += 1

	def maxPlayer(self, state, depth, alpha, beta):
		# The max player gets to choose the move
		self._nodeCount += 1
		self._childCount += 1

		if state.gameOver():
			return state.getScore()
			
		actions = self.moveOrder(state)

		if depth == 0:
			return self.heuristic(state)

		self._parentCount += 1
		best = -10000
		for a in actions:
			if not self.timeRemaining(): return None
			result = state.move(a)
			v = self.minPlayer(result, depth-1, alpha, beta)
			if v is None: return None
			if v > best:
				best = v
			if best >= beta:
				return best
			if best > alpha:
				alpha = best
				
		return best

	def minPlayer(self, state, depth, alpha, beta):
		# The min player chooses where to add the extra tile and whether it is a 2 or a 4
		self._nodeCount += 1
		self._childCount += 1

		if state.gameOver():
			return state.getScore()
			
		actions = self.moveOrder(state)

		if depth == 0:
			return self.heuristic(state)

		self._parentCount += 1
		best = 1e6
		for (t,v) in state.possibleTiles():
			if not self.timeRemaining(): return None
			result = state.addTile(t,v)
			v = self.maxPlayer(result, depth-1, alpha, beta)
			if v is None: return None
			if v < best:
				best = v
			if best <= alpha:
				return best
			if best < beta:
				beta = best			
		return best

	def heuristic(self, state):
		board = state._board

		empty = board.count(0)

		max_tile = max(board)
		corners = [board[0], board[3], board[12], board[15]]
		max_in_corner = 1 if max_tile in corners else 0
		

		merge = 0
		for i, v in enumerate(board):
			if v == 0:
				continue
			if (i % 4) != 3 and v == board[i + 1]:
				merge += 1
			if i < 12 and v == board[i + 4]:
				merge += 1

		board = state._board
		b = [board[i:i+4] for i in range(0, 16, 4)]
		
		weights = [[6, 5, 4, 3], [5, 4, 3, 2], [4, 3, 2, 1], [3, 2, 1, 0]]
		gradient = 0
		for r in range(4):
			for c in range(4):
				gradient += (2 ** b[r][c]) * weights[r][c]

		smooth = 0
		for r in range(4):
			for c in range(3):
				smooth -= abs(b[r][c] - b[r][c+1])
		for r in range(3):
			for c in range(4):
				smooth -= abs(b[r][c] - b[r+1][c])
				
		return (state.getScore() + empty * 100 + max_in_corner * 1000 + merge * 50 + gradient + smooth * 10)
		
	def moveOrder(self, state):
		return state.actions()

	def stats(self):
		print(f'Average depth: {self._depthCount/self._count:.2f}')
		print(f'Branching factor: {self._childCount / self._parentCount:.2f}')
