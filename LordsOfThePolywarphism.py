import time
import random
import tkinter as tk

random.seed(time.time())
soldiersList = []
allSoldiers = []
# Aktif tüm askerleri ve oyuna yerleştirilmiş tüm askerleri tutacak iki liste.
# Tüm sınıflar tarafından erişilebilir olmaları için global olarak atandılar.



# Oyun tahtası sınıfı.
class GameBoard:
    def __init__(self, root, rows, columns, playerCount):
        self.root = root
        self.rows = rows
        self.columns = columns
        self.playerCount = playerCount
        self.playerList = []
        self.round = 1

        self.posList = []
        self.firstGuardiansPosList = [[25, 25],
                                      [25, (self.columns * 50) - 25],
                                      [(self.rows * 50) - 25, 25],
                                      [(self.rows * 50) - 25, (self.columns * 50) - 25]]

        self.clickedX = None
        self.clickedY = None
        self.currentPlayer = None

        for i in range(playerCount):
            player = Player(i + 1)
            self.playerList.append(player)

        self.canvas = tk.Canvas(root, width=columns * 50, height=rows * 50, bg="grey")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self._click)
        # Oyun tahtası tek bir butona sahip. Yerleştirmeler oyuncunun mouse'unun koordinatları alınarak yapılıyor.

        self.draw_board()
        self._round_system()


    def _repaint(self):
        for player in self.playerList:
            self._search_green_squares(player)
            # Fonksiyonu kullanarak askerlerin etrafındaki yeşil karoları belirle.

            for greenSquare in player.playerGreenSquares:
                posX = greenSquare[0]
                posY = greenSquare[1]

                self.canvas.create_rectangle(posX + 25, posY + 25, posX - 25, posY - 25, outline="black",
                                             fill=player.secondColor)
                self.canvas.create_text(posX, posY, text=".")
                # Aramadan sonra elde ettiğin güncellenmiş yeşil karo listesini kullanarak yeşil karoları boya.

        for soldiers in soldiersList:
            soldierPosX = soldiers.xCoord
            soldierPosY = soldiers.yCoord

            self.canvas.create_rectangle(soldierPosX + 25, soldierPosY + 25, soldierPosX - 25,
                                         soldierPosY - 25, outline="black", fill="gray99")
            self.canvas.create_text(soldierPosX, soldierPosY, text=f"{soldiers.name[0]}{soldiers.place}",
                                    fill=soldiers.team)
            # Terhis edilmemiş askerlerin bulunduğu karoları yeniden doldur.


    def _paint_grey_squares(self, target):
        possibleGreenSquares = [[target.xCoord - 50, target.yCoord - 50],
                                [target.xCoord, target.yCoord - 50],
                                [target.xCoord + 50, target.yCoord - 50],
                                [target.xCoord - 50, target.yCoord],
                                [target.xCoord, target.yCoord],
                                [target.xCoord + 50, target.yCoord],
                                [target.xCoord - 50, target.yCoord + 50],
                                [target.xCoord, target.yCoord + 50],
                                [target.xCoord + 50, target.yCoord + 50]]
        # Ölen askerin etrafında bulunabilecek olası yeşil karo koordinatlarını tutan bir liste.

        for i in self.playerList:
            if [target.xCoord, target.yCoord] in i.playerSoldiersList:
                i.playerSoldiersList.remove([target.xCoord, target.yCoord])
                i.playerSoldiersDict[target.name].remove([target.xCoord, target.yCoord])

        self.posList.append([target.xCoord, target.yCoord])
        soldiersList.remove(target)
        # Ölen askeri kullanılan tüm listelerden çıkart.
        # Askerin koordinatlarını aktif koordinatlar listesine ekle.

        for i in soldiersList:
            if target in i.targetsInReach:
                i.targetsInReach.remove(target)
                # Oyun tahtasındaki her askerin çevresindeki askerlerin listesini tutan listelerine eriş,
                # Bu listeden ölen askeri çıkart.

        for possibleSquare in possibleGreenSquares:
            if possibleSquare in self.currentPlayer.playerGreenSquares:
                self.currentPlayer.playerGreenSquares.remove(possibleSquare)
                # Askerin etrafındaki karoları aktif yeşil karolar listesinden çıkart.

        self._search_green_squares(self.currentPlayer)
        # Aktif yeşil karolar için yeniden arama yap.

        for greySquare in possibleGreenSquares:
            posX = greySquare[0]
            posY = greySquare[1]

            self.canvas.create_rectangle(posX + 25, posY + 25, posX - 25, posY - 25,
                                         outline="black",
                                         fill="grey")
            self.canvas.create_text(posX, posY, text=".")
        # Çıkarılan askerin bulunduğu karoyla birlikte etrafındaki 9 karonun rengini de gri yap.

        for row in range(self.rows):
            for col in range(self.columns):
                x1 = col * 50
                y1 = row * 50
                x2 = x1 + 50
                y2 = y1 + 50

                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                self.canvas.create_text(x2 - 25, y2 - 25, text=".")
                # Izgara zemini oluştur ve karoların ortasına nokta ekle.


    def _click(self, event):
        x, y = event.x, event.y
        # Oyucunun tıkladığı pikselin x ve y koordinatlarını al.

        col = x // 50
        row = y // 50

        xOut, yOut = (col * 50) + 25, (row * 50) + 25
        self.clickedX, self.clickedY = xOut, yOut
        # Oyuncunun tıklayacığı pikselin tam olarak kutucuğun orta noktasına gelme ihtimali oldukça zor.
        # Bu yüzden önce kutucuğun alanını tanıttık.
        # Tıklanılan bölgeyle ilişkili kutucuğu işaretle.

        self.action_menu(
            f"Sıra:{self.currentPlayer.color}\nAltın: {self.currentPlayer.balance}\nHak: {self.currentPlayer.moveCount}\nTur: {self.round}")
        # Aksiyon menüsünü oluşturmak için gerekli fonksiyonu çağır ve oyuncunun bilgilerini bu menüye yazdır.


    def _search_green_squares(self, player):
        player.playerGreenSquares.clear()
        # Herhangi bir karoyu eklemeden önce listeyi temizle

        for soldier in soldiersList:
            if soldier.team == player.color:
                possibleGreenSquares = [[soldier.xCoord - 50, soldier.yCoord - 50],
                                        [soldier.xCoord,      soldier.yCoord - 50],
                                        [soldier.xCoord + 50, soldier.yCoord - 50],
                                        [soldier.xCoord - 50, soldier.yCoord],
                                        [soldier.xCoord + 50, soldier.yCoord],
                                        [soldier.xCoord - 50, soldier.yCoord + 50],
                                        [soldier.xCoord,      soldier.yCoord + 50],
                                        [soldier.xCoord + 50, soldier.yCoord + 50]]
                # Olası yeşil karoların pozisyonlarını tutan bir liste.

                for positions in possibleGreenSquares:
                    if (positions[0] < 0) or (positions[1] < 0) or (positions[0] > self.rows * 50) \
                    or (positions[1] > self.columns * 50) or (positions not in self.posList) or (positions in player.playerGreenSquares):
                        continue
                        # Eğer possibleGreenSquares listesindeki pozisyonlar oyun tahtasının sınırlarının dışına çıkıyorsa ya da
                        # pozisyon aktif pozisyonlar listesinde değilse (posList) ya da pozisyon halihazırda yeşil karolar listesindeyse
                        # pozisyonu eklemeden pas geç.

                    else:
                        player.playerGreenSquares.append(positions)
                        # Yukarıdaki şartlardan hiçbiri sağlanmazsa, pozisyonun bulunduğu karo yeşil karodur.


    def _decide_the_winner(self, winner, option):
        self.playerList.clear()
        print("\x1b[38;5;10m-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-")

        if option == 0:
            print(winner.color, "tek başına hayatta kalarak kazandı!")
        # Eğer oyuncu tek başına hayatta kalarak kazandıysa bu bloğa gir.

        elif option == 1:
            print(winner.color, "oyun tahtasının %60'ından fazlasını ele geçirerek kazandı!")
        # Eğer oyuncu tek başına hayatta kalarak kazandıysa bu bloğa gir.

        print("-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-\n")
        print("\x1b[38;5;214mOyun tamamlandı.")

        exit(-1)


    def _decide_the_loser(self, loser, option):
        self.playerList.remove(loser)
        self.currentPlayer = self.playerList[0]
        # Önce oyuncuyu oyuncu listesinden çıkar ve sırayı diğer oyuncuya ver.
        print("\x1b[38;5;1m-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-")

        for soldier in allSoldiers:
            if soldier.team == loser.color and soldier in soldiersList:
                self._paint_grey_squares(soldier)
                # Oyuncunun tüm askerlerinin bulunduğu karoları ve yeşil karolarını griye boya.

                del soldier
                # Askeri sil.

        self._repaint()
        # Tahtayı yeniden boya.

        if option == 0:
            print(loser.color, "tüm askerleri öldürüldüğü için kaybetti!")

        if option == 1:
            print(loser.color, "çok fazla pas geçtiği için kaybetti!")

        print("-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-o-\n")

        del loser
        # Oyuncuyu sil.


    def _check_skips(self, skippedRounds):
        if len(skippedRounds) >= 3:
            for i in range(len(skippedRounds)):
                if skippedRounds[i - 2] + 2 == skippedRounds[i - 1] + 1 == skippedRounds[i]:
                    return True

            return False

        # Eğer sana gelen listede art arda bulunan üç raunt varsa True, yoksa False döndür.


    def _round_system(self):
        if self.currentPlayer is not None and len(self.currentPlayer.playerSoldiersList) == 0:
            self._decide_the_loser(self.currentPlayer, 0)
            # Eğer oyuncunun askeri yoksa, oyuncuyu oyundan at.

        if len(self.playerList) == 1:
            self._decide_the_winner(self.playerList[0], 0)
            # Eğer oyuncu, oyuncu listesinde tek kaldıysa oyuncuyu galip ilan et.

        if self.currentPlayer is not None and len(self.currentPlayer.playerSoldiersList) >= (
                self.rows * self.columns * 60 // 100):
            self._decide_the_winner(self.currentPlayer, 1)
            # Eğer oyuncu tahtanın %60'ını ya da daha fazlasını ele geçirirse, oyuncuyu galip ilan et.

        if self.currentPlayer is None or self.currentPlayer.moveCount == 0:
            self.currentPlayer = self.playerList[0]
            self.playerList.remove(self.currentPlayer)
            self.playerList.append(self.currentPlayer)
            # Hakkı biten oyuncuyu listenin en sonuna at.

        if self._check_skips(self.currentPlayer.skippedRounds) is True:
            self._decide_the_loser(self.currentPlayer, 1)
            # Eğer oyuncu 3 tur üst üste pas geçerse, oyuncuyu oyundan at.

        if self.currentPlayer.playerNum == 1 and self.currentPlayer.moveCount == 0:
            print(f"\x1b[38;5;15m---------------------------------------------\n"
                  f"{self.round}. Savaş")

            self.round += 1

            for player in self.playerList:
                player.balance += 10
                player.balance += len(player.playerSoldiersList)

                player.moveCount = 2
                # Her oyuncunun asker yerleştirme hakkını 2'ye çıkart.
                # Savaş aşaması başladığında konsola yazdır,
                # Raunt sayısını 1 arttır ve her oyuncuya verilmesi gereken altın miktarını ver.

            for soldier in soldiersList:
                if soldier.health > 0:
                    if isinstance(soldier, Medic):
                        soldier.heal()
                        # Eğer asker listesindeki ilk asker bir Sıhhiyeciyse saldırı değil iyileştirme komutu kullan.

                    else:
                        soldier.attack()
                        # Eğer asker Sıhhiyeci değilse, saldırı komutunu kullan.

                if soldier.killedTargets != 0:
                    for target in soldier.killedTargets:
                        if target in soldiersList:
                            self._paint_grey_squares(target)
                            # Eğer asker savaş esnasında birini öldürürse ve öldürülen hedef asker listesinden çıkartılmadıysa,
                            # askeri listeden çıkart.

                            self._repaint()
                            # Oyun tahtasını hayatta kalan askerler için yeniden boya.

                            del target
                            # Ölen askerin nesnesini sil.
            print("---------------------------------------------\n")


    def draw_board(self):
        for row in range(self.rows):
            for col in range(self.columns):
                x1 = col * 50
                y1 = row * 50
                x2 = x1 + 50
                y2 = y1 + 50

                self.posList.append([x2 - 25, y2 - 25])
                # Karoların orta noktalarını muhafız seçiminde aynı karoları kullanmamak için bir listede tut.

                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black")
                self.canvas.create_text(x2 - 25, y2 - 25, text=".")
                # Izgara zemini oluştur ve karoların ortasına nokta ekle.

        for selectedPlayer in self.playerList:
            firstGuardian = Guardian()
            # Sıradan bir oyuncu al ve muhafız oluştur.

            guardianPos = random.choice(self.firstGuardiansPosList)
            guardianPosX = guardianPos[0]
            guardianPosY = guardianPos[1]

            firstGuardian.xCoord = guardianPosX
            firstGuardian.yCoord = guardianPosY
            firstGuardian.team = selectedPlayer.color
            firstGuardian.secondColor = selectedPlayer.secondColor
            firstGuardian.place = len(allSoldiers) + 1
            # Muhafız için konum belirle ve muhafızın özelliklerini tanımla

            selectedPlayer.playerSoldiersDict["Muhafız"].append(guardianPos)
            soldiersList.append(firstGuardian)
            allSoldiers.append(firstGuardian)
            # Muhafızın konumunu oyuncunun askerler sözlüğünün Muhafız kısmına ekle.

            self.firstGuardiansPosList.remove(guardianPos)
            selectedPlayer.playerSoldiersList.append([guardianPosX, guardianPosY])
            self.posList.remove(guardianPos)
            self._search_green_squares(selectedPlayer)
            # Kullanılabilir pozisyonlar listesinden muhafızın konumunu çıkar

            selectedPlayer.firstGuardianPosX = guardianPosX
            selectedPlayer.firstGuardianPosY = guardianPosY
            # İlk muhafızlar için rastgele x ve y koordinatları seç ve bunları oyuncu nesnesinin ilk muhafızının
            # x ve y koordinatlarına ata. Peşinden bu koordinatları koordinat listesinden sil.

            # Eğer bunu yapmazsan muhafızlar üst üste binebilir.

            for j in range(3, 0, -1):
                secondY1 = guardianPosY + 125 - (j * 50)
                secondY2 = guardianPosY + 75 - (j * 50)

                for k in range(3, 0, -1):
                    secondX1 = guardianPosX + 125 - (k * 50)
                    secondX2 = guardianPosX + 75 - (k * 50)

                    self.canvas.create_rectangle(secondX1, secondY1, secondX2, secondY2, outline="black",
                                                 fill=selectedPlayer.secondColor)
                    self.canvas.create_text(secondX2 + 25, secondY2 + 25, text=".")
                    # Muhafızların yerleştirildiği konumların etrafındaki karoları açık yeşile boya ve ortalarına nokta ekle.

            guardianPosX = selectedPlayer.firstGuardianPosX
            guardianPosY = selectedPlayer.firstGuardianPosY

            self.canvas.create_rectangle(guardianPosX + 25, guardianPosY + 25, guardianPosX - 25, guardianPosY - 25,
                                         outline="black", fill="gray99")
            self.canvas.create_text(guardianPosX, guardianPosY, text=f"M{firstGuardian.place}",
                                    fill=selectedPlayer.color)
            # Muhafızların bulunduğu karoyu açık maviye boya ve isimlerini karoya yaz.


    def action_menu(self, message):

        new_window = tk.Toplevel(self.root)
        new_window.title("Aksiyon Menüsü")

        label = tk.Label(new_window, text=message)

        button_text = "Muhafız yetiştir: 10 altın"
        button = tk.Button(new_window, text=button_text,
                           command=lambda text=button_text: self.recruit(new_window, Guardian(), self.clickedX,
                                                                         self.clickedY))
        button.pack()

        button_text = "Okçu yetiştir: 20 altın"
        button = tk.Button(new_window, text=button_text,
                           command=lambda text=button_text: self.recruit(new_window, Archer(), self.clickedX,
                                                                         self.clickedY))
        button.pack()

        button_text = "Topçu yetiştir: 50 altın"
        button = tk.Button(new_window, text=button_text,
                           command=lambda text=button_text: self.recruit(new_window, Artilleryman(), self.clickedX,
                                                                         self.clickedY))
        button.pack()

        button_text = "Atlı yetiştir: 30 altın"
        button = tk.Button(new_window, text=button_text,
                           command=lambda text=button_text: self.recruit(new_window, Cavalry(), self.clickedX,
                                                                         self.clickedY))
        button.pack()

        button_text = "Sıhhiyeci yetiştir: 10 altın"
        button = tk.Button(new_window, text=button_text,
                           command=lambda text=button_text: self.recruit(new_window, Medic(), self.clickedX,
                                                                         self.clickedY))
        button.pack()

        button_text = "Terhis et"
        button = tk.Button(new_window, text=button_text,
                           command=lambda text=button_text: self.demobilizate(new_window, self.clickedX, self.clickedY))
        button.pack()

        button_text = "Pas geç"
        button = tk.Button(new_window, text=button_text, command=lambda text=button_text: self.skip(new_window))
        button.pack()

        button_text = "Geri dön"
        button = tk.Button(new_window, text=button_text, command=lambda text=button_text: new_window.destroy())
        button.pack()

        label.pack()
        # Asker yetiştirme ve aksiyon menüsü.


    def recruit(self, window, soldier, clickedX, clickedY):
        player = self.currentPlayer

        self._search_green_squares(player)
        if player.balance < soldier.cost:
            new_window = tk.Toplevel(self.root)
            new_window.title("Uyarı!")
            label = tk.Label(new_window, text="Yetersiz altın!")
            label.pack()
            window.destroy()

        if player.moveCount == 0:
            new_window = tk.Toplevel(self.root)
            new_window.title("Uyarı!")
            label = tk.Label(new_window, text="Hakkın bitti!")
            label.pack()
            window.destroy()
            # Eğer olur da bir hata oluşup pencere kapanmazsa, oyuncunun işlem yapmasına izin verme.

        if [clickedX, clickedY] not in player.playerGreenSquares:
            new_window = tk.Toplevel(self.root)
            new_window.title("Uyarı!")
            label = tk.Label(new_window, text="Buraya erişimin yok!")
            label.pack()
            window.destroy()
            # Eğer oyuncu yeşil karelerin dışında erişmemesi gereken bir yere tıklarsa, oyuncuyu uyar.

        if [clickedX, clickedY] not in self.posList:
            new_window = tk.Toplevel(self.root)
            new_window.title("Uyarı!")
            label = tk.Label(new_window, text="Burada halihazırda bir asker var!")
            label.pack()
            window.destroy()
            # Eğer oyuncu yeşil karelerin dışında erişmemesi gereken bir yere tıklarsa, oyuncuyu uyar.

        if player.balance >= soldier.cost and player.moveCount > 0 and [clickedX, clickedY] in player.playerGreenSquares \
                and [clickedX, clickedY] in self.posList:
            player.balance -= soldier.cost
            player.moveCount -= 1
            player.playerSoldiersDict[soldier.name].append([clickedX, clickedY])
            player.playerSoldiersList.append([clickedX, clickedY])

            soldier.team = player.color
            soldier.secondColor = player.secondColor
            soldier.xCoord = clickedX
            soldier.yCoord = clickedY

            soldiersList.append(soldier)
            allSoldiers.append(soldier)
            self.posList.remove([clickedX, clickedY])
            # Eğer oyuncunun askeri yetiştirmeye yetecek kadar parası, asker yetiştirme hakkı varsa
            # ve tıklanılan karo yeşil karo ise, bu karoda asker yok ise askeri karoya koy, maliyetini oyuncudan al,
            # oyuncunun hakkını 1 azalt, askerin konumunu ayarla, oyundaki asker listesine askeri ekle,
            # ve aktif pozisyonlar listesinden askerin koordinatlarını çıkart.

            for j in range(3, 0, -1):
                secondY1 = soldier.yCoord + 125 - (j * 50)
                secondY2 = soldier.yCoord + 75 - (j * 50)

                for k in range(3, 0, -1):
                    secondX1 = soldier.xCoord + 125 - (k * 50)
                    secondX2 = soldier.xCoord + 75 - (k * 50)

                    self.canvas.create_rectangle(secondX1, secondY1, secondX2, secondY2, outline="black",
                                                 fill=player.secondColor)
                    self.canvas.create_text(secondX2 + 25, secondY2 + 25, text=".")
            # Yeşile boyama işlemi. draw_board() fonksiyonunda kullanılan ile aynı.

            soldier.place = len(allSoldiers)

            for soldiers in soldiersList:
                soldierPosX = soldiers.xCoord
                soldierPosY = soldiers.yCoord

                self.canvas.create_rectangle(soldierPosX + 25, soldierPosY + 25, soldierPosX - 25,
                                             soldierPosY - 25,
                                             outline="black", fill="gray99")
                self.canvas.create_text(soldierPosX, soldierPosY, text=f"{soldiers.name[0]}{soldiers.place}",
                                        fill=soldiers.team)

                # Karolar yeşile boyandıktan sonra bazı askerlerin üstü kapanabilir.
                # Bunu önlemek için tüm askerlerin pozisyonlarını yeniden açık maviye boya.

        self._round_system()
        window.destroy()
        # Raunt sistemini çağır ve aksiyon menüsünü kapatmaya zorla.


    def demobilizate(self, window, clickedX, clickedY):
        player = self.currentPlayer

        if self.round == 1:
            new_window = tk.Toplevel(self.root)
            new_window.title("Uyarı!")
            label = tk.Label(new_window, text="İlk turda asker terhis edemezsin!")
            label.pack()
            window.destroy()
            # İlk rauntta asker terhis edilemez, edilirse oyuncu oyunu kaybeder.
            # Bu yüzden ilk rauntta terhise izin verme.

        if [clickedX, clickedY] in player.playerSoldiersList and self.round != 1:
            for soldier in soldiersList:
                if [soldier.xCoord, soldier.yCoord] == [clickedX, clickedY]:

                    player.balance += soldier.cost * 80 / 100
                    self._paint_grey_squares(soldier)
                    # Askerin yetiştirilme maaliyetinin %80'ini oyuncuya geri ver.
                    # Askerin etrafındaki yeşil karoları ve kendi karosunu griye boya.

                    self._repaint()
                    # Tahtayı yeniden boya

                self._round_system()
                del soldier
                window.destroy()
                # Çıkartılan askerin nesnesini sil, raunt sistemini çağır ve aksiyon menüsünü kapatmaya zorla.

        elif [clickedX, clickedY] not in player.playerSoldiersList:
            new_window = tk.Toplevel(self.root)
            new_window.title("Uyarı!")
            label = tk.Label(new_window, text="Burada terhis edilecek asker yok!")
            label.pack()
            window.destroy()
            # Karoda asker yoksa oyuncuyu uyar.


    def skip(self, window):
        if self.currentPlayer.moveCount == 2:
            self.currentPlayer.skippedRounds.append(self.round)
            # Eğer oyuncu 1 hamle yapmayı tercih ederse, bu raundu pas geçilmiş raunt sayma.

        self.currentPlayer.moveCount = 0
        self._round_system()
        # Oyuncunun hakkını 0' a eşitle ve raunt sistemini çağır.

        window.destroy()
        # Aksiyon menüsünü kapatmaya zorla.



# Oyuncu sınıfı.
class Player:
    def __init__(self, playerNum):
        self.playerNum = playerNum
        self.priority = playerNum
        self.balance = 200

        self.firstGuardianPosX = None
        self.firstGuardianPosY = None

        self.playerSoldiersDict = {"Muhafız": [],
                                   "Okçu": [],
                                   "Topçu": [],
                                   "Atlı": [],
                                   "Sıhhiyeci": []}

        self.playerGreenSquares = []
        self.playerSoldiersList = []
        self.moveCount = 2
        self.skippedRounds = []

        if playerNum == 1:
            self.color = "red"
            self.secondColor = "brown1"

        elif playerNum == 2:
            self.color = "blue"
            self.secondColor = "deep sky blue"

        elif playerNum == 3:
            self.color = "green"
            self.secondColor = "SpringGreen2"

        elif playerNum == 4:
            self.color = "yellow"
            self.secondColor = "goldenrod1"



# Asker sınıfı.
class Soldier:
    def __init__(self, name, cost, health, rangeHorizontal, rangeVertical, rangeDiagonal, dmg=None, dmgPercentage=None,
                 team=None, xCoord=None, yCoord=None):
        self.name = name
        self.cost = cost
        self.health = health
        self.rangeHorizontal = rangeHorizontal
        self.rangeVertical = rangeVertical
        self.rangeDiagonal = rangeDiagonal
        self.dmg = dmg
        self.dmgPercentage = dmgPercentage

        self.place = None
        self.secondColor = None

        self.team = team
        self.xCoord = xCoord
        self.yCoord = yCoord

        self.targetsInReach = []
        self.killedTargets = []

    def detect_targets(self):
        for target in soldiersList:
            if isinstance(self, Medic):
                if (self.team != target.team) or (target.xCoord == self.xCoord and target.yCoord == self.yCoord) or (
                        target in self.targetsInReach):
                    continue
                    # Eğer sen Sıhhiyeci sınıfındansan ve hedefin senin takımından değil ise,
                    # ya da hedefin x ve y koordinatları senin koordinatlarınla aynıysa,
                    # ya da hedef halihazırda listedeyse, hedefi pas geç.

            elif isinstance(self, Medic) is False:
                if (self.team == target.team) or (target.xCoord == self.xCoord and target.yCoord == self.yCoord) or (
                        target in self.targetsInReach):
                    continue
                    # Eğer sen Sıhhiyeci sınıfından değilsen ve hedefin senin takımındansa,
                    # ya da hedefin x ve y koordinatları senin koordinatlarınla aynıysa,
                    # ya da hedef halihazırda listedeyse, hedefi pas geç.

            if abs(target.xCoord - self.xCoord) <= self.rangeHorizontal * 50 and abs(target.yCoord - self.yCoord) == 0:
                self.targetsInReach.append(target)

            if abs(target.xCoord - self.xCoord) == 0 and abs(target.yCoord - self.yCoord) <= self.rangeVertical * 50:
                self.targetsInReach.append(target)

            if abs(target.xCoord - self.xCoord) == abs(target.yCoord - self.yCoord):
                if abs(target.xCoord - self.xCoord) <= self.rangeDiagonal * 50 and abs(
                        target.yCoord - self.yCoord) <= self.rangeDiagonal * 50:
                    self.targetsInReach.append(target)

    def attack(self):
        self.detect_targets()
        # Yukarıdaki fonksiyonu kullanarak etrafını tara.

        for target in self.targetsInReach:
            if target.team != self.team:
                if self.dmg is not None:
                    target.health -= self.dmg
                    # Eğer etrafındaki asker düşmanınsa ve yüzdelik hasar yerine mutlak hasar vurabiliyorsan,
                    # düşmanın canını hasarın kadar azalt.

                elif self.dmgPercentage is not None:
                    dmgDealt = target.health * self.dmgPercentage / 100
                    target.health -= dmgDealt

            if target.health <= 0:
                print(f"{target.name}{target.place}, {self.name}{self.place} tarafından öldürüldü!")
                self.killedTargets.clear()
                # Askerin tek rauntta öldürdüğü askerleri bu listede tutmak istiyoruz.
                # Bu yüzden ekleme yapmadan önce listeyi boşalt.

                self.killedTargets.append(target)



# Muhafız sınıfı.
class Guardian(Soldier):
    def __init__(self):
        super().__init__("Muhafız", 10, 80, 1, 1, 1, 20)

    def detect_targets(self):
        super().detect_targets()

    def attack(self):
        super().attack()



# Okçu sınıfı.
class Archer(Soldier):
    def __init__(self):
        super().__init__("Okçu", 20, 30, 2, 2, 2, None, 60)

    # !Aşırı yüklenmiş fonksiyon!
    def detect_targets(self):
        super().detect_targets()
        sorted(self.targetsInReach, key=lambda soldier: soldier.health, reverse=True)
        # Ebeveyn fonksiyonu çalıştır sonrasında hedefleri canlarına göre büyükten küçüğe sırala.

        availableTargets = self.targetsInReach[:3]
        self.targetsInReach = availableTargets
        # Sıralanmış hedeflerin ilk 3'ünü al.

    def attack(self):
        super().attack()



# Topçu sınıfı.
class Artilleryman(Soldier):
    def __init__(self):
        super().__init__("Topçu", 50, 30, 2, 2, 0, None, 100)

    # !Aşırı yüklenmiş fonksiyon!
    def detect_targets(self):
        super().detect_targets()
        sorted(self.targetsInReach, key=lambda soldier: soldier.health, reverse=True)
        # Ebeveyn fonksiyonu çalıştır sonrasında hedefleri canlarına göre büyükten küçüğe sırala.

        availableTargets = self.targetsInReach[:1]
        self.targetsInReach = availableTargets
        # Sıralanmış hedeflerin ilkini al.

    def attack(self):
        super().attack()



# Süvari sınıfı.
class Cavalry(Soldier):
    def __init__(self):
        super().__init__("Atlı", 30, 40, 0, 0, 3, 30)

    # !Aşırı yüklenmiş fonksiyon!
    def detect_targets(self):
        super().detect_targets()
        sorted(self.targetsInReach, key=lambda soldier: soldier.cost, reverse=True)
        # Ebeveyn fonksiyonu çalıştır sonrasında hedefleri maliyetlerine göre büyükten küçüğe sırala.

        availableTargets = self.targetsInReach[:2]
        self.targetsInReach = availableTargets
        # Sıralanmış hedeflerin ilk ikisini al.

    def attack(self):
        super().attack()



# Sıhhiye sınıfı.
class Medic(Soldier):
    def __init__(self):
        super().__init__("Sıhhiyeci", 10, 100, 2, 2, 2)

    # !Aşırı yüklenmiş fonksiyon!
    def detect_targets(self):
        super().detect_targets()
        sorted(self.targetsInReach, key=lambda soldier: soldier.health)
        # Ebeveyn fonksiyonu çalıştır sonrasında hedefleri canlarına göre küçükten büyüğe sırala.

        availableTargets = self.targetsInReach[:3]
        self.targetsInReach = availableTargets
        # Sıralanmış hedeflerin ilk üçünü al.

    def heal(self):
        self.detect_targets()
        for target in self.targetsInReach:
            if target.team == self.team:
                healAmount = target.health * 50 / 100
                target.health += healAmount
                # Takım arkadaşının can miktarının %50'si kadar iyileştir.

    def attack(self):
        self.heal()
        # Aksilikleri önlemek için saldırı fonksiyonunu da iyileştirme fonksiyonunu çağırması için aşırı yükledik.



# Başlatma fonksiyonu.
def start():
    while True:
        try:
            inputList = input("Enter the board size: ").split(",")
            boardSizeRows, boardSizeCols = int(inputList[0]), int(inputList[1])

            if len(inputList) != 2 or boardSizeRows < 8 or boardSizeRows > 32 or boardSizeCols < 8 or boardSizeCols > 32:
                raise ValueError("Invalid input")
            break
            # Geçerli girdi alınırsa döngüyü kır.

        except ValueError or IndexError:
            print("Invalid input. Please enter two integers separated by a comma (row,col) between 8 and 32.")

    while True:
        try:
            playerCount = int(input("Enter the number of players: "))

            if playerCount < 2 or playerCount > 4:
                raise ValueError("Invalid player count")

            break
            # Geçerli girdi alınırsa döngüyü kır.

        except ValueError:
            print("Invalid input. Please enter an integer between 2 and 4.")


    root = tk.Tk()
    root.title("Lords Of The Polywarphism")
    game_board = GameBoard(root, boardSizeRows, boardSizeCols, playerCount)
    root.mainloop()


start()