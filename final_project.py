#//////////////////////////import libraries////////////////////////////////////
from camera2 import camera_cal
import cv2
import DoBotArm2 as Dbt
import DobotDllType as dType
import chess
from stockfish import Stockfish
#//////////////////////////////////////////////////////////////////////////////

class chess_game:
    def __init__(self):
        engine_path = r"C:\Users\AAST\Desktop\chess _project_dont_touch21\stockfish_15.1_win_x64_avx2\stockfish-windows-2022-x86-64-avx2.exe"
        self.engine = Stockfish(engine_path)
        self.board = chess.Board()
        self.engine.set_fen_position(self.board.fen())
        self.api = dType.load() #define api
        self.flag = 0 # witch dobot
        self.dict , self.inverse= self.callibration_list()
        self.piece = None
        self.home =  [(127.2997,-169.2213),(164.0931,-170.4302)]
    #///////calibration/////////
    def callibration_list(self):
        image = [cv2.imread(r"C:\Users\AAST\Desktop\chess _project_dont_touch21\CameraCalibration 2\images\img21.png")]
        obj = camera_cal(image)
        dict , inverse = obj.callibrate()
        return dict , inverse
    #///////////////////////////
    def get_best_move(self,board):
        self.engine.set_fen_position(board.fen())
        result = self.engine.get_best_move_time(2000)
        return chess.Move.from_uci(result)
    #/////////connect////////////
    def toggle(self):
        list = ["COM4","COM3"]
        homeX = 250
        homeY = 0
        homeZ = 50
        dobot = Dbt.DoBotArm(homeX, homeY, homeZ,list[self.flag])
        return dobot
    # /////////////////////////
    # ////////mov to postion///
    def mov_to(self,dobot,sX,sY,eX,eY):
        self.api = dType.load() 
        #///////pick///////
        dobot.moveArmXY(sX,sY)
        dobot.setGrip(False)
        dobot.pick(-24.8228)
        dobot.setGrip(True)
        dobot.pick(24.8228)
        #//////////////////
        #//////place////////
        dobot.moveArmXY(eX,eY)
        dobot.pick(-24.8228)
        dobot.setGrip(False)
        dobot.pick(24.8228)
        dobot.moveArmXY(self.home[self.flag][0],self.home[self.flag][1])
        dobot.pick(-24.8228)
        dType.DisconnectDobot(self.api)
        return True
    #//////////////////////////
    def remove_piece(self,dobot,X,Y):
        self.api = dType.load() 
        dobot.moveArmXY(X,Y)
        dobot.setGrip(False)
        dobot.pick(-24.8228)
        dobot.setGrip(True)
        dobot.pick(24.8228)
        #//////////////////
        #//////place////////
        dobot.moveArmXY(self.home[self.flag][0],self.home[self.flag][1])
        dobot.pick(-24.8228)
        dobot.setGrip(False)
        dobot.pick(24.8228)
        dobot.moveArmXY(self.home[self.flag][0],self.home[self.flag][1] )
        dobot.pick(-24.8228)
        dType.DisconnectDobot(self.api)
    #////////convert/////////
    def calculate(self, s1, s2, dict):
        armX0 = 156.1945 # given offest values of arm
        armY0 = 56.8971
        armX6 = 275.8459
        armY6 = -64.3035
        difX = (armX6 - armX0) / 6 #width, height of block
        difY = (armY6 - armY0) / 6

        n1 = s1
        n2 = s2

        if (s1 > 6): # map to previous corner if out of boundaries
            n1 = s1 - 1
        if (s2 > 6):
            n2 = s2 - 1

        sx = dict[(n1, n2)][0] # access corner values of x, y in dictionary
        sy = dict[(n1, n2)][1]

        sX = (armX6 - armX0) / (dict[(6, 6)][0] - dict[(0, 0)][0]) #map corner of camera to corner of arm values
        sX = sX * (sx - dict[(0, 0)][0]) + armX0
        sY = (armY6 - armY0) / (dict[(6, 6)][1] - dict[(0, 0)][1])
        sY = sY* (sy - dict[(0, 0)][1]) + armY0

        print(n1, n2)
        print("equation calculation for corner")
        print(sX, sY)

        if (s1 <= 6): #scale from corner to middle of cell to all values 
            sX = sX - difX/2
        else:
            sX = sX + difX/2
        if (s2 <= 6):
            sY = sY - difY/2
        else:
            sY = sY + difY/2

        print("calculated coordinate points")
        print(sX, sY)
    
        return sX, sY    


    def XY(self,move,dict, opposite):
        s1 = self.convert_to_number(move[0]) # range from 0 to 7
        s2 = self.convert_to_number(move[1]) 
        e1 = self.convert_to_number(move[2]) 
        e2 = self.convert_to_number(move[3])
        print("points start to end")
        print(s1, s2, e1, e2)
        # print("desired coordinate points")
        # print(self.gen(s1, s2))

        self.piece = self.board.piece_at(chess.square(e1,e2))
        
        if(opposite): #reflect board for opposite robot
            s1 = 7 - s1 
            s2 = 7 - s2
            e1 = 7 - e1 
            e2 = 7 - e2
            print("points start to end in reverse")
            print(s1, s2, e1, e2)


        sX, sY = self.calculate(s1, s2, dict)
        eX, eY = self.calculate(e1, e2, dict)
        if(opposite):
            #return sX + 35, sY + 32, eX + 35, eY +32
            return sX+40, sY, eX+40, eY
            #return sX , sY, eX, eY
        return sX, sY , eX , eY
    #////////////////////////////////////
    def convert_to_number(self,character):
        if character.isalpha():
            character = character.lower()
            offset = ord('a') 
            return ord(character) - offset
        elif character.isdigit():
            return int(character) - 1
        else:
            raise ValueError("Invalid input. Please enter a letter or a digit.")
    #///////////main/////////////
    def main(self):
        while not self.board.is_game_over():
            print(self.board)
            # Bot 1's turn
            if self.board.turn == chess.WHITE:
                self.flag =0
                dobot = game.toggle()
                move = self.get_best_move(self.board)
                print("move robot 1 is moving: ")
                print(move)
                sX , SY , eX , eY = self.XY(str(move), self.dict,0)
                print(sX , SY , eX , eY)
                print(self.piece)
                if self.piece is not None:
                    self.remove_piece(dobot,eX,eY)
                self.mov_to(dobot , sX , SY , eX , eY)
                self.board.push(move)
            # Bot 2's turn
            else:
                self.flag =1
                dobot = game.toggle()
                move = self.get_best_move(self.board)
                print("move robot 2 is moving: ")
                print(move)
                sX , SY , eX , eY = self.XY(str(move), self.inverse,1)
                print(sX , SY , eX , eY)
                print(self.piece)
                if self.piece is not None:
                    self.remove_piece(dobot,eX,eY)
                self.mov_to(dobot , sX , SY , eX , eY)
                self.board.push(move)
            print(self.board)
        print("the game is end")



if __name__ == '__main__':
    game = chess_game()
    game.main()
    # print(game.dict)
    # print("------------------------------------------")
    # print(game.inverse)
    # game.flag = 1
    # dobot = game.toggle()
    # move = 'd2d3'
    # sx , sy,ex,ey = game.XY(move,game.inverse , 1)
    # game.mov_to(dobot, sx , sy,ex,ey)
    # game.flag =0
    # dobot = game.toggle()
    # game.mov_to(dobot ,185.5604 ,  -54.9343 ,224.8669 , -53.8758)
    # game.flag =1
    # dobot = game.toggle()
    # game.mov_to(dobot ,213.2336 ,  39.0453 ,251.2796 , 42.0632)
    # game.flag =0
    # dobot = game.toggle()
    # game.mov_to(dobot , 182.4694,  -15.6336 ,221.6035 ,  -13.3254)
    # game.flag =1
    # dobot = game.toggle()
    # game.mov_to(dobot ,212.0807, -43.3070 ,234.9510 ,  -44.8192)
    # game.flag =0
    # dobot = game.toggle()
    # game.remove_piece(dobot ,244.7507 , -36.2185 )
    # dobot = game.toggle()
    # game.mov_to(dobot ,224.8669 , -53.8758 ,244.7507 , -36.2185 )



    
    





















