from numpy.random import normal, random_integers, poisson
import numpy as np
from random import randint, random
from scipy.stats import truncnorm
from math import ceil
from sklearn.linear_model import Ridge
from cards.models import *

class CardCreatorAgent:

    def __init__(self, subset_size=100):
        self._load_card_subset(subset_size)
        self._learn_coeffs()

    def _load_card_subset(self, subset_size):
        print("CardCreator: Learning to evaluate card values for a random subset of size" + str(subset_size))

        try:
            data = np.load("heathstonedata.npy")
            print("CardCreator: Loaded card data from cache")
        except Exception:
            print("CardCreator: Did not find cached data, reading from DB (This WILL take ~10 minutes)")
            data =  _data_as_numpy_array()
            print("CardCreator: Loading complete, caching data")
            np.save("heathstonedata.npy", data)
            print("CardCreator: Caching complete")

        sub_indices = np.random.choice(max(len(data), subset_size), subset_size)

        self._cards = np.ascontiguousarray(data[:, 1:][sub_indices], dtype=np.float)

    def _memoize(self, card):
        row = self._card_as_row(card)
        random_index = randint(len(self._cards) - 1)

        print("CardCreator: Replacing card at index {} with a new card".format(random_index))

        self._cards[random_index] = row
        self._cards = np.ascontiguousarray(self._cards, dtype=np.float)
        self._learn_coeffs


    def _card_as_row(self, card):
        row = [
            card['mana'],
            card['health'],
            card['attack'],
            0,
            0,
        ]
        for ctype in CardType.objects.all().order_by('id'):
            if card['type'] == ctype.name:
                row.append(1)
            else:
                row.append(0)

        for race in Race.objects.all().order_by('id'):
            if card['race'] == race.name:
                row.append(1)
            else:
                row.append(0)

        for mechanic in Mechanic.objects.all().order_by('id'):
            for card_mechanic in card['mechanics']:
                if card_mechanic[1] == mechanic.id:
                    row.append(card_mechanic[2])
                else:
                    row.append(0)
        return np.array(row)


    def _learn_coeffs(self):
        y = np.ascontiguousarray(self._cards[:, 0], dtype=np.float)
        X = np.ascontiguousarray(self._cards[:, 1:], dtype=np.float)

        print("CardCreator: Learning")
        model = Ridge(alpha=0.00001)
        model.fit(X, y)

        print("CardCreator: Learning complete with accuracy {}".format(model.score(X, y)))

        coeffs = model.coef_

        self.health_coeff = coeffs[0]
        self.attack_coeff = coeffs[1]
        #durability_coeff = coeffs[2]
        #weapon_attack_coeff =coeffs[3]


    def _generate_card(self):
        card = {}
        card_val = 0

        card['mana'] = int(round(normal(2.5, 1.5)))

        card_val += self._generate_mechanics(card)
        card_val += self._generate_health_and_attack(card, card["mana"] - card_val)

        card['player_class'] = "All"
        #card['image'] = "http://i.imgur.com/TqFP5w7.jpg"

        card['value'] = card_val
        self._define_rarity(card)
        self._generate_name(card)
        self._set_random_race(card)
        self._set_random_image(card)
        card['type'] = "Minion"

        print("CardCreator: Created card {}".format(card))
        return card

    def act(self):
        return self._generate_card()

    def _set_random_image(self, card):
        #Just a copy from previous one atm
        urls = ["http://i.imgur.com/TqFP5w7.jpg", "http://i.imgur.com/4bg2pMF.jpg", "http://i.imgur.com/x2ndWAb.jpg", "http://i.imgur.com/yGlLavd.jpg", "http://i.imgur.com/3A3Hm64.jpg", "http://i.imgur.com/SUi7GBl.png", "http://i.imgur.com/wRlbv6Q.jpg", "http://i.imgur.com/MGRDrvd.jpg", "http://i.imgur.com/zBZn0s2.jpg", "http://i.imgur.com/mVhe2DJ.jpg", "http://i.imgur.com/fKnRsBL.jpg", "http://i.imgur.com/Y0BdNfL.jpg", "http://i.imgur.com/JiIkLqm.jpg", "http://i.imgur.com/KQXKBoY.jpg", "http://i.imgur.com/ylzazdp.jpg", "http://i.imgur.com/Kgvx28W.jpg", "http://i.imgur.com/D4hbwgN.png", "http://i.imgur.com/nO1iXjY.jpg", "http://i.imgur.com/jOb1c5a.jpg", "http://i.imgur.com/UnoQ4w0.jpg", "http://i.imgur.com/4i4fCcT.jpg", "http://i.imgur.com/VricKcA.jpg", "http://i.imgur.com/Pgx8vOx.jpg", "http://i.imgur.com/sd9UKjH.png", "http://i.imgur.com/UeDpz5E.jpg", "http://i.imgur.com/frydGDH.jpg", "http://i.imgur.com/xgCpv67.jpg", "http://i.imgur.com/jtOxM68.jpg", "http://i.imgur.com/Y7wxJNl.jpg", "http://i.imgur.com/D4sqeM6.jpg", "http://i.imgur.com/sGXLPq7.jpg", "http://i.imgur.com/T2vpRSu.jpg", "http://i.imgur.com/KmsXX6s.jpg", "http://i.imgur.com/tr7s5xy.jpg", "http://i.imgur.com/eBtmpi3.jpg", "http://i.imgur.com/OKaYz0s.jpg", "http://i.imgur.com/JQzNFDA.jpg", "http://i.imgur.com/bMSaBNp.jpg", "http://i.imgur.com/IT8eBGq.jpg", "http://i.imgur.com/LHAOwdg.jpg", "http://i.imgur.com/U6hxcUY.jpg", "http://i.imgur.com/rrNVamb.png", "http://i.imgur.com/alSh4Lq.jpg", "http://i.imgur.com/KwMmZ4j.jpg", "http://i.imgur.com/ha8M8HC.jpg", "http://i.imgur.com/gqlfJ3S.jpg", "http://i.imgur.com/O1KoHjN.jpg", "http://i.imgur.com/rxtXz0e.jpg", "http://i.imgur.com/JyQfqYM.jpg", "http://i.imgur.com/rJ5Trsk.jpg", "http://i.imgur.com/UNyLkNS.jpg", "http://i.imgur.com/I6EzW0r.jpg", "http://i.imgur.com/PACBiHT.jpg", "http://i.imgur.com/9EqALOg.jpg", "http://i.imgur.com/jkTcR4q.png", "http://i.imgur.com/c63Qepu.png", "http://i.imgur.com/LU5C5e5.png", "http://i.imgur.com/Y8Sd2pi.jpg", "http://i.imgur.com/ohLAfTa.jpg", "http://i.imgur.com/hvd3uAA.jpg", "http://i.imgur.com/0zFBXPN.jpg", "http://i.imgur.com/aJnZU8c.jpg", "http://i.imgur.com/kKFxlFp.jpg", "http://i.imgur.com/WOAv2CS.jpg", "http://i.imgur.com/YJL4Azj.jpg", "http://i.imgur.com/F6EcVs4.jpg", "http://i.imgur.com/EUbtJJx.jpg", "http://i.imgur.com/9XsK7sa.jpg", "http://i.imgur.com/V33bpL1.png", "http://i.imgur.com/v54WQIq.jpg", "http://i.imgur.com/ag7AFp4.jpg", "http://i.imgur.com/MaKd7dG.png", "http://i.imgur.com/u3SwYav.jpg", "http://i.imgur.com/4xzvSXX.jpg", "http://i.imgur.com/HrXBLq5.png", "http://i.imgur.com/UNVdxRv.jpg", "http://i.imgur.com/dtsG629.jpg", "http://i.imgur.com/OCmNdXy.jpg", "http://i.imgur.com/8Esun8T.png", "http://i.imgur.com/lMDrLvS.jpg", "http://i.imgur.com/3GTJ9nv.jpg", "http://i.imgur.com/oiiU5IO.jpg", "http://i.imgur.com/NOkzDFQ.jpg", "http://i.imgur.com/n8wSeiF.jpg", "http://i.imgur.com/daFHOYE.jpg", "http://i.imgur.com/xdup90h.jpg", "http://i.imgur.com/Cl1NiKN.jpg", "http://i.imgur.com/rPJq0aZ.jpg", "http://i.imgur.com/wuWQ2O0.png", "http://i.imgur.com/IiC7NtY.jpg", "http://i.imgur.com/73KvmsY.jpg", "http://i.imgur.com/AfVpKDA.png", "http://i.imgur.com/AUZ3js9.png", "http://i.imgur.com/3LghlRR.jpg", "http://i.imgur.com/PAU4X2Q.jpg", "http://i.imgur.com/gawX170.jpg", "http://i.imgur.com/WlwAazG.jpg", "http://i.imgur.com/FuOfVFv.png", "http://i.imgur.com/yUJJRTB.png", "http://i.imgur.com/4HOdtbQ.jpg", "http://i.imgur.com/WfgHpFa.jpg", "http://i.imgur.com/4jtW6ms.jpg", "http://i.imgur.com/8DULIPM.jpg", "http://i.imgur.com/EnIQUmZ.jpg", "http://i.imgur.com/XBwbvX0.jpg", "http://i.imgur.com/xp5ob3g.jpg", "http://i.imgur.com/Ocosihv.png", "http://i.imgur.com/zqAfXPT.jpg", "http://i.imgur.com/ZKdbSNA.jpg", "http://i.imgur.com/xGqg2fG.jpg", "http://i.imgur.com/e3wArLP.jpg", "http://i.imgur.com/q1FdKhf.png", "http://i.imgur.com/YX7FLKj.jpg", "http://i.imgur.com/texzhaP.jpg", "http://i.imgur.com/SDzHEC0.png", "http://i.imgur.com/Qabg5uy.jpg", "http://i.imgur.com/OGm4v9n.jpg", "http://i.imgur.com/gncMTfQ.png", "http://i.imgur.com/lCh8baH.jpg", "http://i.imgur.com/0qGXVaP.jpg", "http://i.imgur.com/ppfk9rk.jpg", "http://i.imgur.com/unzTEgX.jpg", "http://i.imgur.com/37wre2b.jpg", "http://i.imgur.com/4U3BIyZ.png", "http://i.imgur.com/yeVj7eK.png", "http://i.imgur.com/dLbsupy.jpg", "http://i.imgur.com/OQuA1IH.jpg", "http://i.imgur.com/xvLjX9k.jpg", "http://i.imgur.com/fGubCbw.jpg", "http://i.imgur.com/sOuBcNT.png", "http://i.imgur.com/504NPS1.jpg", "http://i.imgur.com/l7Ng5kb.jpg", "http://i.imgur.com/8GMFzJf.jpg", "http://i.imgur.com/s3deXJN.png", "http://i.imgur.com/9uDzmF1.jpg", "http://i.imgur.com/CAa1aLv.jpg", "http://i.imgur.com/h5H2ca1.png", "http://i.imgur.com/FMgMI2W.jpg", "http://i.imgur.com/7fQWoTD.png", "http://i.imgur.com/IeWqelb.jpg", "http://i.imgur.com/eFr8CA4.jpg", "http://i.imgur.com/M4h8yLD.jpg", "http://i.imgur.com/ZqCiGiL.jpg", "http://i.imgur.com/MZSE12B.png", "http://i.imgur.com/acM34Tn.jpg", "http://i.imgur.com/4kqApIE.jpg", "http://i.imgur.com/7gjUTSm.jpg", "http://i.imgur.com/UMDYUsz.jpg", "http://i.imgur.com/eQ4U7zu.png", "http://i.imgur.com/92d8v1j.jpg", "http://i.imgur.com/POZ7nuF.jpg", "http://i.imgur.com/Z4XTa6F.png", "http://i.imgur.com/FiU4Z59.jpg", "http://i.imgur.com/m4LEHOa.jpg", "http://i.imgur.com/odbNjVu.png", "http://i.imgur.com/E4xzrtI.jpg", "http://i.imgur.com/ZYam3hc.png", "http://i.imgur.com/GKTXaNx.png", "http://i.imgur.com/XVTZvRF.jpg", "http://i.imgur.com/lAHoP27.jpg", "http://i.imgur.com/UUh7ybj.jpg", "http://i.imgur.com/DxPLhSk.png", "http://i.imgur.com/h6UjG2W.jpg", "http://i.imgur.com/k4pvjrO.jpg", "http://i.imgur.com/6wR0rl3.jpg", "http://i.imgur.com/8RmmMpN.jpg", "http://i.imgur.com/DByCYGI.png", "http://i.imgur.com/9J3Esbu.png", "http://i.imgur.com/FybDWhB.jpg", "http://i.imgur.com/R5jVGXt.jpg", "http://i.imgur.com/QJC4h2v.png", "http://i.imgur.com/WGLtrkb.jpg", "http://i.imgur.com/6uEr8Qv.jpg", "http://i.imgur.com/ZvpMYbt.jpg", "http://i.imgur.com/a0hiMxT.jpg", "http://i.imgur.com/TcpkDQr.png", "http://i.imgur.com/6O71Qkp.jpg", "http://i.imgur.com/d9BMyKT.jpg", "http://i.imgur.com/Lvdy9QK.jpg", "http://i.imgur.com/YtnTPCF.jpg", "http://i.imgur.com/E17PRlH.jpg", "http://i.imgur.com/wm4HRLd.jpg", "http://i.imgur.com/yjHFNBB.jpg", "http://i.imgur.com/BLtxfUj.png", "http://i.imgur.com/P0tQ6kr.jpg", "http://i.imgur.com/wSitlK3.jpg", "http://i.imgur.com/7mroHVb.png", "http://i.imgur.com/5FJR1rc.jpg", "http://i.imgur.com/2P0N0lc.jpg", "http://i.imgur.com/VbW5xjb.jpg", "http://i.imgur.com/1v93DuA.jpg", "http://i.imgur.com/wsyplxd.jpg", "http://i.imgur.com/4rGhYoe.jpg", "http://i.imgur.com/RoZeddH.jpg", "http://i.imgur.com/GvCs2Fp.jpg", "http://i.imgur.com/dFRZVBE.jpg", "http://i.imgur.com/kQNbUCP.jpg", "http://i.imgur.com/WhSCZpE.jpg", "http://i.imgur.com/l3WlRmj.jpg", "http://i.imgur.com/jlvdHWm.png", "http://i.imgur.com/nXdK7Ku.png", "http://i.imgur.com/hyJXMay.jpg", "http://i.imgur.com/89NDw94.jpg", "http://i.imgur.com/PQwWPdC.jpg", "http://i.imgur.com/lmvAeMa.jpg", "http://i.imgur.com/tMnfboY.png", "http://i.imgur.com/C8irCGB.png", "http://i.imgur.com/0oc0lGt.jpg", "http://i.imgur.com/OcV4OVM.jpg", "http://i.imgur.com/x3ABhGf.png", "http://i.imgur.com/m0L6wxY.jpg", "http://i.imgur.com/cqZDDbZ.png", "http://i.imgur.com/IfY6CV6.png", "http://i.imgur.com/ajZu51q.png", "http://i.imgur.com/T0wueLj.png", "http://i.imgur.com/lOLEkon.jpg", "http://i.imgur.com/PITr1tU.jpg", "http://i.imgur.com/S1Uk86O.jpg", "http://i.imgur.com/jtIf8Ph.png", "http://i.imgur.com/uuTKmx0.png", "http://i.imgur.com/bYLM3kU.jpg", "http://i.imgur.com/jMn8b5D.jpg", "http://i.imgur.com/YSoviZ6.jpg", "http://i.imgur.com/8CiP39v.png", "http://i.imgur.com/viwcf96.jpg", "http://i.imgur.com/dF325m3.jpg", "http://i.imgur.com/oo6fRF1.png", "http://i.imgur.com/J6tZR3h.jpg", "http://i.imgur.com/1qAt4Ag.jpg", "http://i.imgur.com/KRfXHQt.png", "http://i.imgur.com/vT8KAGD.png", "http://i.imgur.com/MNYKpiy.jpg", "http://i.imgur.com/b91L84Y.jpg", "http://i.imgur.com/EDQMmVo.jpg", "http://i.imgur.com/TBOxNj2.jpg", "http://i.imgur.com/54VH64p.jpg", "http://i.imgur.com/wOifMYW.png", "http://i.imgur.com/oFhBjls.png", "http://i.imgur.com/miT7RNR.jpg", "http://i.imgur.com/OXBcqPH.jpg", "http://i.imgur.com/Jz6DR6s.jpg", "http://i.imgur.com/5h2ocop.jpg", "http://i.imgur.com/vIbXFjX.jpg", "http://i.imgur.com/TtnKS0H.jpg", "http://i.imgur.com/2XVCJ9x.jpg", "http://i.imgur.com/sXslPCK.png", "http://i.imgur.com/HbLyqJz.jpg", "http://i.imgur.com/Ly8wJcB.jpg", "http://i.imgur.com/VhXXnLv.png", "http://i.imgur.com/CmbFdEr.jpg", "http://i.imgur.com/cHpLSYr.jpg", "http://i.imgur.com/dsNbpDz.jpg", "http://i.imgur.com/lEW2BTO.jpg", "http://i.imgur.com/kICH9LV.png", "http://i.imgur.com/DfhrWyi.jpg", "http://i.imgur.com/EUbCeon.jpg", "http://i.imgur.com/r3ghokQ.png", "http://i.imgur.com/VF7UPat.jpg", "http://i.imgur.com/sIK2h2k.jpg", "http://i.imgur.com/ld2598P.png", "http://i.imgur.com/sLrjgrO.jpg", "http://i.imgur.com/8QR1AW9.jpg", "http://i.imgur.com/Tk95TZr.jpg", "http://i.imgur.com/7YraLDY.jpg", "http://i.imgur.com/oHDSqKt.jpg", "http://i.imgur.com/oYOrlDU.png", "http://i.imgur.com/4czAVrT.png", "http://i.imgur.com/IHEVF2I.jpg", "http://i.imgur.com/keTmYTe.jpg", "http://i.imgur.com/dO0k7se.jpg", "http://i.imgur.com/5dpsnmi.jpg", "http://i.imgur.com/6QzUh1G.jpg", "http://i.imgur.com/KQzvBhM.png", "http://i.imgur.com/BN4guqa.jpg", "http://i.imgur.com/JR5Mh3e.jpg", "http://i.imgur.com/5rChY57.png", "http://i.imgur.com/Gp5tBm7.jpg", "http://i.imgur.com/QhijHKy.jpg", "http://i.imgur.com/2gcDgrv.png", "http://i.imgur.com/zMzW83N.jpg", "http://i.imgur.com/iaYTS7s.png", "http://i.imgur.com/3kT6YEl.jpg", "http://i.imgur.com/BSsDJOQ.jpg", "http://i.imgur.com/PAhKo1B.jpg", "http://i.imgur.com/OyGXpBZ.jpg", "http://i.imgur.com/FyrWtIF.jpg", "http://i.imgur.com/T5QvQr2.jpg", "http://i.imgur.com/5fmNLDM.jpg", "http://i.imgur.com/OsSratT.jpg", "http://i.imgur.com/MIdSvPR.png", "http://i.imgur.com/bCMzW45.png", "http://i.imgur.com/2RVknMw.jpg", "http://i.imgur.com/IsORqdD.png", "http://i.imgur.com/LJ72Srv.jpg", "http://i.imgur.com/FQishuG.jpg", "http://i.imgur.com/XjsSWEs.jpg", "http://i.imgur.com/uk4Zjkz.png", "http://i.imgur.com/6nB0tUo.jpg", "http://i.imgur.com/1LTuuYT.jpg", "http://i.imgur.com/lcfYNws.jpg", "http://i.imgur.com/2TGx6Lm.jpg", "http://i.imgur.com/Cq98unJ.png", "http://i.imgur.com/l1Nb7xm.jpg", "http://i.imgur.com/EKQxdTS.png", "http://i.imgur.com/zaeXLjb.png", "http://i.imgur.com/EgLh4rJ.jpg", "http://i.imgur.com/FD4i4xh.jpg", "http://i.imgur.com/F1x4Ekr.jpg", "http://i.imgur.com/TUgXntM.png", "http://i.imgur.com/iTnm7al.png", "http://i.imgur.com/8ptAX0L.png", "http://i.imgur.com/x7x5m08.jpg", "http://i.imgur.com/nZ9iwem.png", "http://i.imgur.com/ddIowaM.png", "http://i.imgur.com/AicGPoh.jpg", "http://i.imgur.com/TM3t4b5.jpg", "http://i.imgur.com/b4FA6dt.jpg", "http://i.imgur.com/klPDvll.png", "http://i.imgur.com/ChoWHAM.png", "http://i.imgur.com/TucZ8Rh.png", "http://i.imgur.com/vzZJFGS.png", "http://i.imgur.com/DtC77Cb.png", "http://i.imgur.com/AvvTedH.png", "http://i.imgur.com/8Wu4dps.jpg", "http://i.imgur.com/w2dzneZ.jpg", "http://i.imgur.com/9CKTnBm.jpg", "http://i.imgur.com/t5MzSZG.png", "http://i.imgur.com/41iAx34.png", "http://i.imgur.com/qMnEtpE.jpg", "http://i.imgur.com/pfPpXhG.jpg", "http://i.imgur.com/NhMi3ot.jpg", "http://i.imgur.com/xwDmJjz.jpg", "http://i.imgur.com/4sDGBe1.jpg", "http://i.imgur.com/7FaZ3gR.jpg", "http://i.imgur.com/hQJ3lby.jpg", "http://i.imgur.com/rBWcYm1.jpg", "http://i.imgur.com/gonLwEG.jpg", "http://i.imgur.com/P2FvCMV.jpg", "http://i.imgur.com/v7LCGsh.jpg", "http://i.imgur.com/KR7GiNf.jpg", "http://i.imgur.com/MqZTC6j.jpg", "http://i.imgur.com/PhpidY5.png", "http://i.imgur.com/BLw7mnU.jpg", "http://i.imgur.com/wNtDt5L.png", "http://i.imgur.com/54bj4Qu.jpg", "http://i.imgur.com/0Dizn52.jpg", "http://i.imgur.com/IXm13yv.jpg", "http://i.imgur.com/yvEmdhL.png", "http://i.imgur.com/My5XPcJ.jpg", "http://i.imgur.com/GrosVfV.jpg", "http://i.imgur.com/cffP9dY.png", "http://i.imgur.com/n3CNE70.png", "http://i.imgur.com/Y9fZwH2.jpg", "http://i.imgur.com/I7QM1if.jpg", "http://i.imgur.com/clGvSbt.jpg", "http://i.imgur.com/nFfG55f.png", "http://i.imgur.com/uX5NGnb.png", "http://i.imgur.com/bemDu23.jpg", "http://i.imgur.com/q0qlDqz.jpg", "http://i.imgur.com/LsXQiHF.jpg", "http://i.imgur.com/mxbprQh.jpg", "http://i.imgur.com/sNG5j9N.png", "http://i.imgur.com/sX9IgUx.jpg", "http://i.imgur.com/IoF9201.jpg", "http://i.imgur.com/aqMMbGn.jpg", "http://i.imgur.com/vnnRk3M.jpg", "http://i.imgur.com/Et2qetj.jpg", "http://i.imgur.com/NbAZqEf.jpg", "http://i.imgur.com/omNXKKC.jpg", "http://i.imgur.com/fLpxHOy.png", "http://i.imgur.com/IYiYvLe.png", "http://i.imgur.com/rDlMy5e.jpg", "http://i.imgur.com/Caj0QKL.png", "http://i.imgur.com/5XENqNW.jpg", "http://i.imgur.com/fZ5Okiq.png", "http://i.imgur.com/19N2wr0.png", "http://i.imgur.com/Hy3LHDN.jpg", "http://i.imgur.com/auRSn2T.jpg", "http://i.imgur.com/XaDEswN.jpg", "http://i.imgur.com/PQj8OZt.jpg", "http://i.imgur.com/M44HvJP.jpg", "http://i.imgur.com/N304UiL.png", "http://i.imgur.com/1ibaq0d.jpg", "http://i.imgur.com/HvToN6P.jpg", "http://i.imgur.com/EoZe5d1.jpg", "http://i.imgur.com/vygTtIZ.jpg", "http://i.imgur.com/nmyWhFx.jpg", "http://i.imgur.com/C0YyKYe.png", "http://i.imgur.com/awWtPEt.jpg", "http://i.imgur.com/Ejbw83L.jpg", "http://i.imgur.com/0XfMFYU.jpg", "http://i.imgur.com/DMmbHfH.jpg", "http://i.imgur.com/9kwaezX.jpg", "http://i.imgur.com/IB6Bkso.jpg", "http://i.imgur.com/E3IzgIl.jpg", "http://i.imgur.com/nK1UWkd.jpg", "http://i.imgur.com/b3n8q28.jpg", "http://i.imgur.com/qHS7EJN.png", "http://i.imgur.com/9v6klR1.jpg", "http://i.imgur.com/GXFcNcG.png", "http://i.imgur.com/Q6dS6kf.jpg", "http://i.imgur.com/tvf8kAa.jpg", "http://i.imgur.com/ed4TtfC.jpg", "http://i.imgur.com/NXyKbl1.jpg", "http://i.imgur.com/JG8UrM4.jpg", "http://i.imgur.com/UtT14lw.jpg", "http://i.imgur.com/fjMEdof.jpg", "http://i.imgur.com/cCWVpYU.jpg", "http://i.imgur.com/c84RKbW.jpg", "http://i.imgur.com/34E9vuM.png", "http://i.imgur.com/BEcAIMm.jpg", "http://i.imgur.com/R7iGm9p.jpg", "http://i.imgur.com/RVwplwk.jpg", "http://i.imgur.com/reguvRV.jpg", "http://i.imgur.com/gMjHd8z.jpg", "http://i.imgur.com/Be79bkW.jpg", "http://i.imgur.com/aoUcFuq.jpg", "http://i.imgur.com/VpXMyuh.jpg", "http://i.imgur.com/FSxCP9o.png", "http://i.imgur.com/MNMG2wU.png", "http://i.imgur.com/e1USk8T.jpg", "http://i.imgur.com/7L0QqSi.jpg", "http://i.imgur.com/kUC3nPB.jpg", "http://i.imgur.com/S9znYEp.jpg", "http://i.imgur.com/dF8aX7s.jpg", "http://i.imgur.com/2D5bzyF.jpg", "http://i.imgur.com/qCjW5zx.png", "http://i.imgur.com/BicychG.jpg", "http://i.imgur.com/UlVROUE.png", "http://i.imgur.com/3Cl9oQj.png", "http://i.imgur.com/lsRjAmf.jpg", "http://i.imgur.com/6TkJPqD.jpg", "http://i.imgur.com/oxszafd.jpg", "http://i.imgur.com/5Z1fKPt.jpg", "http://i.imgur.com/DjKjNAI.jpg", "http://i.imgur.com/lHmolEv.png", "http://i.imgur.com/xYLgBYr.jpg", "http://i.imgur.com/BpMXxyv.jpg", "http://i.imgur.com/HfAeOJN.jpg", "http://i.imgur.com/WnirzD3.jpg", "http://i.imgur.com/ztMAR2N.jpg", "http://i.imgur.com/kQBKcXw.jpg", "http://i.imgur.com/kN0ESeR.png", "http://i.imgur.com/rrSHisS.jpg", "http://i.imgur.com/IdOTkar.png", "http://i.imgur.com/22QaQVU.jpg", "http://i.imgur.com/QnsykkD.jpg", "http://i.imgur.com/RpA5XQw.jpg", "http://i.imgur.com/6XmK0Eg.jpg", "http://i.imgur.com/xdd7Otv.jpg", "http://i.imgur.com/Ozn1XgD.jpg", "http://i.imgur.com/yEpTQt8.jpg", "http://i.imgur.com/LXVhOQQ.jpg", "http://i.imgur.com/LUopdb4.jpg", "http://i.imgur.com/pfLiNNw.png", "http://i.imgur.com/Uc8GdEZ.jpg", "http://i.imgur.com/GVLmuri.png", "http://i.imgur.com/jWmHy7M.jpg", "http://i.imgur.com/svvCCTb.png", "http://i.imgur.com/FQvOcQc.jpg", "http://i.imgur.com/tX3iMtw.jpg", "http://i.imgur.com/rqRBoSa.jpg", "http://i.imgur.com/SxHdAxr.png", "http://i.imgur.com/0kUgBjw.jpg", "http://i.imgur.com/HYQ9l0Q.png", "http://i.imgur.com/45FVV7f.jpg", "http://i.imgur.com/CB0AuAW.jpg", "http://i.imgur.com/ZeGMQeK.jpg", "http://i.imgur.com/DsSvbCL.jpg", "http://i.imgur.com/CpW25F6.png", "http://i.imgur.com/scsI8g4.png", "http://i.imgur.com/7wOPd1Z.jpg", "http://i.imgur.com/rnVIrX6.jpg", "http://i.imgur.com/dbeaHNy.jpg", "http://i.imgur.com/E9sbHNT.png", "http://i.imgur.com/Bs4xFfk.jpg", "http://i.imgur.com/UC1u6mP.jpg", "http://i.imgur.com/BFUrfCX.png", "http://i.imgur.com/TjXNpaR.jpg", "http://i.imgur.com/ajT6BOQ.png", "http://i.imgur.com/VuD95GA.png", "http://i.imgur.com/K2ZzapE.jpg", "http://i.imgur.com/meoTsEp.png", "http://i.imgur.com/lfBOlLq.jpg", "http://i.imgur.com/yY406RV.jpg", "http://i.imgur.com/csf8YSr.png", "http://i.imgur.com/suIOnbQ.jpg", "http://i.imgur.com/RGH8pHR.png", "http://i.imgur.com/1XZlFLw.png", "http://i.imgur.com/ozEYlSJ.jpg", "http://i.imgur.com/3bymTwx.png", "http://i.imgur.com/iVjkafo.png", "http://i.imgur.com/Qscj4xi.png", "http://i.imgur.com/UC8WzJ8.png", "http://i.imgur.com/V18AgBe.jpg", "http://i.imgur.com/SGXfOom.jpg", "http://i.imgur.com/GqQbZEn.png", "http://i.imgur.com/BoPiAfb.png", "http://i.imgur.com/HN5cWEc.png", "http://i.imgur.com/nOap2jp.jpg", "http://i.imgur.com/uWjOq1S.png", "http://i.imgur.com/0Ov80J1.jpg", "http://i.imgur.com/ygDlmqR.jpg", "http://i.imgur.com/T0sZRrn.jpg", "http://i.imgur.com/IR41kWU.png", "http://i.imgur.com/mfjPjrD.jpg", "http://i.imgur.com/SAxoWeG.jpg", "http://i.imgur.com/qoLCTeZ.png", "http://i.imgur.com/g55SACr.jpg", "http://i.imgur.com/5X6RfEP.png", "http://i.imgur.com/9EZ1PLi.png", "http://i.imgur.com/J18E88b.jpg", "http://i.imgur.com/kw7y7VB.png", "http://i.imgur.com/yI5QHNo.png", "http://i.imgur.com/8pnsNMn.jpg", "http://i.imgur.com/UHScp68.jpg", "http://i.imgur.com/SK8PkNp.png", "http://i.imgur.com/c2GoTJr.png", "http://i.imgur.com/sSQ9xZy.jpg", "http://i.imgur.com/PNF6s77.jpg", "http://i.imgur.com/FrLtXk5.png", "http://i.imgur.com/z09Gomk.jpg", "http://i.imgur.com/gkIwLd2.jpg", "http://i.imgur.com/bbXl5e9.png", "http://i.imgur.com/l50FSgy.jpg", "http://i.imgur.com/h0hjYoM.png", "http://i.imgur.com/GwLX6eF.jpg", "http://i.imgur.com/BhfBCVD.png", "http://i.imgur.com/RM4AKHy.png", "http://i.imgur.com/0pDxIiS.jpg", "http://i.imgur.com/v6bLuPr.jpg", "http://i.imgur.com/1G7GsuD.jpg", "http://i.imgur.com/RSLHYXJ.png", "http://i.imgur.com/KHu18pm.png", "http://i.imgur.com/BreGEvF.png", "http://i.imgur.com/gUk2ZJj.jpg", "http://i.imgur.com/PSk1COo.jpg", "http://i.imgur.com/HSyk2RF.png", "http://i.imgur.com/qJvZXAf.jpg", "http://i.imgur.com/DEksIVD.jpg", "http://i.imgur.com/oNnXY9D.jpg", "http://i.imgur.com/mTlcqCl.jpg", "http://i.imgur.com/jqgUQks.jpg", "http://i.imgur.com/HsxcwlN.png", "http://i.imgur.com/sD17Awl.png", "http://i.imgur.com/AdhMn5B.png", "http://i.imgur.com/erJY3NF.png", "http://i.imgur.com/WRGNUmS.png", "http://i.imgur.com/a4nPmRe.jpg", "http://i.imgur.com/S3H5ncT.png", "http://i.imgur.com/BhNUhx5.jpg", "http://i.imgur.com/oJbgVwk.jpg", "http://i.imgur.com/MHrDld8.jpg", "http://i.imgur.com/0Jx89EI.jpg", "http://i.imgur.com/ADm3YT1.png", "http://i.imgur.com/oFKK3MW.png", "http://i.imgur.com/bxTwvBj.png", "http://i.imgur.com/pQy7QlT.png", "http://i.imgur.com/O514ddC.jpg", "http://i.imgur.com/LTkOEic.jpg", "http://i.imgur.com/EYCWZgQ.jpg", "http://i.imgur.com/Gnnzgv5.jpg", "http://i.imgur.com/OSP6NIm.png", "http://i.imgur.com/GtxZJ2e.jpg", "http://i.imgur.com/V4dp2VC.jpg", "http://i.imgur.com/gwxRtrB.png", "http://i.imgur.com/UVNkMoT.png", "http://i.imgur.com/by3pnnh.jpg", "http://i.imgur.com/NoGVwMW.jpg", "http://i.imgur.com/rzXazVy.png", "http://i.imgur.com/93sTeqU.jpg", "http://i.imgur.com/zpffabx.png", "http://i.imgur.com/dpftO62.jpg", "http://i.imgur.com/W4FqDrM.png", "http://i.imgur.com/JEu7ttU.png", "http://i.imgur.com/K9d55Qr.jpg", "http://i.imgur.com/D6OrXrl.png", "http://i.imgur.com/pCAIlMU.png", "http://i.imgur.com/osmpScY.png", "http://i.imgur.com/fsKj9Nr.png", "http://i.imgur.com/l7LN9yE.png", "http://i.imgur.com/iJ5qbGv.png", "http://i.imgur.com/U5J9dyz.jpg", "http://i.imgur.com/dXUOy5A.png", "http://i.imgur.com/hegsHr6.png", "http://i.imgur.com/CQy6EfM.jpg", "http://i.imgur.com/dWSQO67.png", "http://i.imgur.com/E4VmLEq.png", "http://i.imgur.com/LTO9YeB.png", "http://i.imgur.com/cGWfT69.png", "http://i.imgur.com/mysOis5.png", "http://i.imgur.com/5CVRurR.png", "http://i.imgur.com/etqY0Qk.png", "http://i.imgur.com/wUcvpH6.png", "http://i.imgur.com/KS4KvmM.png", "http://i.imgur.com/vwfPPD0.png", "http://i.imgur.com/dKxR9br.png", "http://i.imgur.com/YrMXGle.jpg", "http://i.imgur.com/E88GSdD.jpg", "http://i.imgur.com/xKJx6v0.png", "http://i.imgur.com/KIXntKu.png", "http://i.imgur.com/rgGoAkQ.png", "http://i.imgur.com/ifISr91.png", "http://i.imgur.com/oRaYBuU.png", "http://i.imgur.com/GiyIO3a.png", "http://i.imgur.com/G0C9oh2.png", "http://i.imgur.com/XwhWIlu.png", "http://i.imgur.com/KoBQ0UF.jpg", "http://i.imgur.com/h39Ikpk.png", "http://i.imgur.com/dRCwWVm.png", "http://i.imgur.com/S7u0JO4.png", "http://i.imgur.com/vIQv3VJ.png", "http://i.imgur.com/SVAXWo7.jpg", "http://i.imgur.com/I2xgnum.png", "http://i.imgur.com/4iH81Nl.png", "http://i.imgur.com/9rA75O7.png", "http://i.imgur.com/PkQpYmY.jpg", "http://i.imgur.com/EIHwfPC.jpg", "http://i.imgur.com/WLWV22B.png", "http://i.imgur.com/hQJ3CBW.png", "http://i.imgur.com/Gu84BKy.jpg", "http://i.imgur.com/zhuo8TP.jpg", "http://i.imgur.com/3nYiCfw.jpg", "http://i.imgur.com/bF5BoPQ.jpg", "http://i.imgur.com/pN9As3c.jpg", "http://i.imgur.com/eiNaYOu.jpg", "http://i.imgur.com/wrAa5zC.jpg", "http://i.imgur.com/2zGDs7X.jpg", "http://i.imgur.com/ABq1x7F.jpg", "http://i.imgur.com/mUZ0doz.jpg", "http://i.imgur.com/cEtkLqX.jpg", "http://i.imgur.com/RVO3v1I.jpg", "http://i.imgur.com/qVHKl61.jpg", "http://i.imgur.com/tX2JIXi.png", "http://i.imgur.com/oX3Egss.jpg", "http://i.imgur.com/9RtpiWD.jpg", "http://i.imgur.com/jCTJ1q9.jpg", "http://i.imgur.com/m5Gtlec.jpg", "http://i.imgur.com/smNIcEM.jpg", "http://i.imgur.com/cG7Lb4g.jpg", "http://i.imgur.com/l6CiGWO.jpg", "http://i.imgur.com/YPjd4JZ.jpg", "http://i.imgur.com/IFLZT6n.jpg", "http://i.imgur.com/fjVQ4SP.jpg", "http://i.imgur.com/jTo0Mw7.jpg", "http://i.imgur.com/wKrR1Tl.jpg", "http://i.imgur.com/AmLCW6E.jpg", "http://i.imgur.com/vx7umAu.png", "http://i.imgur.com/x9xSfWq.png", "http://i.imgur.com/3LZiwxX.jpg", "http://i.imgur.com/YflgH6S.jpg", "http://i.imgur.com/r91tT12.jpg", "http://i.imgur.com/nSn0AzY.jpg", "http://i.imgur.com/Vkc766z.jpg", "http://i.imgur.com/wmPZnPM.jpg", "http://i.imgur.com/vinNteU.jpg", "http://i.imgur.com/xEBQOGh.jpg", "http://i.imgur.com/DkRMHIN.jpg", "http://i.imgur.com/mzEoTtL.jpg", "http://i.imgur.com/gW7gKXb.jpg", "http://i.imgur.com/cOsvCsO.jpg", "http://i.imgur.com/jSKT5wu.jpg", "http://i.imgur.com/wFJmUyr.jpg", "http://i.imgur.com/mWQeuSD.jpg", "http://i.imgur.com/KSlb51X.jpg", "http://i.imgur.com/pHtEu8x.jpg", "http://i.imgur.com/nNZEROp.jpg", "http://i.imgur.com/KAcmoiW.jpg", "http://i.imgur.com/Yamw24U.jpg", "http://i.imgur.com/Y7oYXw9.jpg", "http://i.imgur.com/acc1g5K.jpg", "http://i.imgur.com/SZpIF9G.jpg", "http://i.imgur.com/6xa7FRC.jpg", "http://i.imgur.com/QJJgFLS.jpg", "http://i.imgur.com/C8ZcXNt.jpg", "http://i.imgur.com/Y5sCIEx.jpg", "http://i.imgur.com/dYBilLw.jpg", "http://i.imgur.com/qkGC4pB.jpg", "http://i.imgur.com/hUQ0CT4.jpg", "http://i.imgur.com/3ydkFNz.jpg", "http://i.imgur.com/9JVXDxr.jpg", "http://i.imgur.com/FZYJo4C.jpg", "http://i.imgur.com/97ieVTp.jpg", "http://i.imgur.com/kq3JZRl.jpg", "http://i.imgur.com/QH5uUKu.png", "http://i.imgur.com/2r7bM4r.png", "http://i.imgur.com/C76qRPR.png", "http://i.imgur.com/k169cEZ.png", "http://i.imgur.com/Pl8HTP7.png", "http://i.imgur.com/M5FtSdb.png", "http://i.imgur.com/s0liOd4.png", "http://i.imgur.com/wn7zDw2.png", "http://i.imgur.com/JqIEvgO.png", "http://i.imgur.com/DEiaoyh.png", "http://i.imgur.com/m1oyhaY.png", "http://i.imgur.com/aMtE7yf.png", "http://i.imgur.com/Cf0XBC2.png", "http://i.imgur.com/DSp5KMC.png", "http://i.imgur.com/eRdnqnD.png", "http://i.imgur.com/kdX81AG.png", "http://i.imgur.com/eW9WtEP.png", "http://i.imgur.com/3lkkm4c.png", "http://i.imgur.com/791hpZf.png", "http://i.imgur.com/HHODy9K.png", "http://i.imgur.com/faJnlMM.png", "http://i.imgur.com/3IVf3UT.png", "http://i.imgur.com/LTag1pg.png", "http://i.imgur.com/LTnYgKc.png", "http://i.imgur.com/LZxsPnn.jpg", "http://i.imgur.com/8XY4VZ8.png", "http://i.imgur.com/VrzGviX.png", "http://i.imgur.com/V5nyyCh.png", "http://i.imgur.com/eSSB3Av.png"]
        card['image'] = urls[randint(0, len(urls)-1)]

    def _set_random_race(self, card):
        #Just a copy from previous one atm
        if random() < 0.5:
            card['race'] = Race.objects.order_by('?').first().name
        if not 'race' in card or card['race'] == "None":
            card['race'] = None

    def _generate_name(self, card):
        #Just a copy from previous one atm
        first = ["Aberrant", "Abusive", "Acidic", "Acolyte", "Addled", "Aldor", "Alexstrasza's", "Am'gam", "Amani", "Ancient", "Angry", "Animated", "Anodized", "Antique", "Anub'ar", "Anubisath", "Arathi", "Arcane", "Argent", "Armored", "Auchenai", "Axe", "Azure", "Bilefin", "Blackwater", "Blackwing", "Bladed", "Blood", "Bloodfen", "Bloodhoof", "Bloodsail", "Bluegill", "Bog", "Bomb", "Boneguard", "Booty Bay", "Boulderfist", "Brave", "Buccaneer", "Burly", "C'Thun's", "Captured", "Carrion", "Chillwind", "Clockwork", "Cobalt", "Cogmaster", "Coldlight", "Coliseum", "Core", "Corrupted", "Crazed", "Cruel", "Cult", "Dalaran", "Dancing", "Dark", "Dark Iron", "Darkscale", "Darkshire", "Darnassus", "Defender", "Defias", "Demented", "Desert", "Dire", "Disciple", "Draenei", "Dragon", "Dragonhawk", "Dragonkin", "Dragonling", "Drakonid", "Dread", "Druid", "Dunemaul", "Dust", "Earthen Ring", "Eater", "Eerie", "Eldritch", "Elven", "Emperor", "Ethereal", "Evil", "Evolved", "Explosive", "Faceless", "Faerie", "Fallen", "Fearsome", "Fel", "Fen", "Fencing", "Fierce", "Fiery", "Fire", "Fireguard", "Flame", "Flametongue", "Flamewreathed", "Flesheating", "Floating", "Flying", "Force-Tank", "Forlorn", "Fossilized", "Frigid", "Frost", "Frostwolf", "Frothing", "Gadgetzan", "Gilblin", "Gnomeregan", "Gnomish", "Goblin", "Goldshire", "Gorillabot", "Grim", "Grimscale", "Grotesque", "Grove", "Guardian", "Gurubashi", "Harvest", "Haunted", "Holy", "Hooded", "Huge", "Hungry", "Ice", "Imp", "Infested", "Injured", "Iron", "Ironbark", "Ironbeak", "Ironforge", "Ironfur", "Jeweled", "Jungle", "Keeper", "Kezan", "King", "King's", "Kirin Tor", "Klaxxi", "Knife", "Knight", "Kobold", "Kor'kron", "Kvaldir", "Lance", "Leper", "Light's", "Lightwarden", "Lil'", "Loot", "Lord", "Lost", "Lowly", "Mad", "Madder", "Magma", "Maiden", "Mana", "Mana Tide", "Master", "Master", "Mechanical", "Metaltooth", "Micro", "Midnight", "Mind Control", "Mire", "Mistress", "Mogor's", "Mogu'shan", "Mounted", "Mukla's", "Murloc", "Museum", "N'Zoth's", "Nerub'ar", "Nerubian", "North Sea", "Northshire", "Novice", "Oasis", "Obsidian", "Ogre", "One-eyed", "Orgrimmar", "Piloted", "Pint-Sized", "Pit", "Polluted", "Possessed", "Priestess", "Questing", "Raging", "Raid", "Ram", "Ravaging", "Ravenholdt", "Razorfen", "Reckless", "Refreshment", "Reliquary", "River", "Rumbling", "Salty", "Savage", "Savannah", "Scarlet", "Scavenging", "Screwjank", "Secretkeeper", "Selfless", "Sen'jin", "Servant", "Shado-Pan", "Shady", "Shattered Sun", "Shieldbearer", "Shielded", "Shifting", "Ship's", "SI:7", "Siege", "Silent", "Silithid", "Silver Hand", "Silverback", "Silvermoon", "Skeram", "Sludge", "Soot", "Sorcerer's", "Southsea", "Sparring", "Spawn", "Spectral", "Spider", "Spiteful", "Squirming", "Stampeding", "Starving", "Steward", "Stoneskin", "Stonesplinter", "Stonetusk", "Stormpike", "Stormwind", "Stranglethorn", "Summoning", "Sunfury", "Target", "Tauren", "Temple", "Tentacle", "Thing", "Thrallmar", "Thunder Bluff", "Timber", "Tinkertown", "Tiny", "Tomb", "Totem", "Tournament", "Tundra", "Tunnel", "Tuskarr", "Twilight", "Twisted", "Unbound", "Undercity", "Unearthed", "Unstable", "Upgraded", "Usher", "Venture Co.", "Violet", "Vitality", "Void", "Volcanic", "Voodoo", "Wailing", "War", "Warhorse", "Warsong", "Water", "Whirling", "Wild", "Windfury", "Wobbling", "Worgen", "Wyrmrest", "Young", "Youthful", "Zealous", "Zombie"]
        second = ["A-3", "Abomination", "Acolyte", "Addict", "Adventurer", "Agent", "Alarm-o-Bot", "Alchemist", "Alchemist", "Alpha", "Amber-Weaver", "Ambusher", "Annoy-o-Tron", "Apothecary", "Apprentice", "Arakkoa", "Arcanist", "Archer", "Archmage", "Arena", "Argus", "Armor", "Armorsmith", "Aspirant", "Assassin", "Attendee", "Auctioneer", "Auto-Barber", "Bat", "Beasts", "Beckoner", "Behemoth", "Belcher", "Below", "Berserker", "Blademaster", "Blastmage", "Boar", "Bodyguard", "Bomber", "Brave", "Brewmaster", "Brute", "Buccaneer", "Buzzard", "C'Thun", "Camel", "Cannon", "Cannon", "Carrier", "Champion", "Cheat", "Chicken", "Chosen", "Chow", "Claw", "Cleric", "Cleric", "Clunker", "Coach", "Cobra", "Cogmaster", "Combatant", "Commander", "Commando", "Conjurer", "Consort", "Corruptor", "Corsair", "Councilman", "Creeper", "Crocolisk", "Crusader", "Crusher", "Cub", "Cultist", "Curator", "Cutpurse", "Darkmender", "Darkshire", "Dealer", "Deathlord", "Deckhand", "Demolisher", "Destroyer", "Destroyer", "Devil", "Devilsaur", "Disguise", "Doctor", "Dog", "Doomcaller", "Doomguard", "Dragon", "Dragonhawk", "Drake", "Dummy", "Duskboar", "Dwarf", "Egg", "Elder", "Elekk", "Elemental", "Elite", "Elune", "Enforcer", "Engine", "Engineer", "Evil", "Evolution", "Exorcist", "Experimenter", "Faceless", "Fang", "Farseer", "Felguard", "Fighter", "First Mate", "Flame", "Flamecaller", "Flamewaker", "Flinger", "Footman", "Frostcaller", "Gang Boss", "Gargoyle", "Geomancer", "Ghoul", "Gnome", "Golem", "Grizzly", "Grove", "Grub", "Grunt", "Guardian", "Harpy", "Healbot", "Healer", "Heckler", "Hero", "Highmane", "Hoarder", "Horror", "Horserider", "Hound", "Houndmaster", "Huckster", "Hunter", "Hyena", "Illuminator", "Imp", "Infantry", "Infernal", "Infiltrator", "Initiate", "Inventor", "Jeeves", "Jormungar", "Jouster", "Juggler", "Keeper", "Kings", "Knight", "Kobold", "Kodo", "Kraken", "Kvaldir", "Lake", "Leader", "Leaper", "Librarian", "Lieutenant", "Lightspawn", "Lightwell", "Lobber", "Lumberer", "Machine", "Mage", "Magi", "Manager", "Master", "MAX", "Mech-Bear-Cat", "Mechanic", "Mechwarper", "Medic", "Mercenary", "Minibot", "Monkey", "Moonkin", "Mystic", "N'Zoth", "Nightblade", "Ninja", "Nullifier", "Ogre", "Ooze", "Oracle", "Owl", "Pain", "Panther", "Partner", "Patriarch", "Patron", "Peacekeeper", "Peddler", "Pillager", "Pirate", "Portal", "Priestess", "Prophet", "Protector", "Psych-o-Tron", "Puddlestomper", "Purifier", "Pyromancer", "Rager", "Raider", "Raptor", "Regent", "Repair Bot", "Rhino", "Rider", "Rider", "Rifleman", "Ringleader", "Robo", "Rocketeer", "Rockjaw", "Runts", "Saber", "Saboteur", "Sapper", "Scarab", "Scientist", "Secretkeeper", "Secrets", "Seeker", "Seer", "Sensei", "Sentinel", "Sergeant", "Shade", "Shade", "Shadowboxer", "Shadows", "Shaman", "Sheep", "Shieldbearer", "Shieldmaiden", "Shieldmasta", "Shredder", "Shrinkmeister", "Skulker", "Smith", "Snake", "Snapjaw", "Snobold", "Snowchugger", "Sorcerer", "Soul", "Soulpriest", "Souls", "Spellbreaker", "Spellslinger", "Spewer", "Spider", "Squidface", "Squire", "Stalker", "Statue", "Stone", "Succubus", "Summoner", "Sunwalker", "Swamp", "Swarmer", "Swords", "Swordsmith", "Tallstrider", "Tank", "Taskmaster", "Tauren", "Teacher", "Tech", "Technician", "Tender", "Tentacle", "Terror", "Tidecaller", "Tidehunter", "Tiger", "Tinyfin", "Toad", "Totem", "Totemcarver", "Totemic", "Trainer", "Trogg", "Uldaman", "Undertaker", "Valiant", "Vendor", "Villager", "Voidcaller", "Voidwalker", "Warbot", "Warden", "Warhorse", "Warlord", "Warrior", "Watcher", "Watchman", "Weaponsmith", "Weblord", "Webspinner", "Whelp", "Wild", "Wildwalker", "Windspeaker", "Wisp", "Wolf", "Wolfrider", "Worgen", "Wraith", "Wrangler", "Wrathguard", "Wyrm", "X-21", "Yeti", "Yogg-Saron", "Zap-o-matic"]

        if random() < 0.66:
            name = first[randint(0, len(first) - 1)] + " "  + second[randint(0, len(second) - 1)]
        else:
            name = second[randint(0, len(second) - 1)]
        if random() < 0.25:
            name += " of the " + second[randint(0, len(second) - 1)]

        #card['name'] = "Teemo's Mushroom"
        card['name'] = name

    def _define_rarity(self, card):
        '''Sets the rarity of the card based on it's manacost and value.

        :param dict card: card to set the rarity to
        '''
        diff = card["value"] - card["mana"]

        if diff < 0.1:
            card["rarity"] = "Common"
        elif diff < 0.2:
            card["rarity"] = "Rare"
        elif diff < 0.3:
            card["rarity"] = "Epic"
        else:
            card["rarity"] = "Legendary"


    def _generate_mechanics(self, card, max_mechanics=5):
        mechanics = list(Mechanic.objects.all().filter(cardmechanic__card__cardType__name__exact="Minion").order_by('value'))

        total_value = 0
        chosen = []

        for i in range(min(poisson(2), max_mechanics)):
            mech = mechanics[random_integers(len(mechanics))-1]

            if "%d" in mech.name:
                d = poisson(2)
                chosen.append((mech.name.replace("%d", str(d)), mech.id, d))
                total_value += (mech.value * d)
            else:
                chosen.append((mech.name, mech.id, 1))
                total_value += mech.value

        card['mechanics'] = chosen
        return total_value

    def _generate_health_and_attack(self, card, mana):
        '''Generates health and attack for a card based on given mana. Mana
        is divided for health and attack by using truncated normal
        distribution.

        :param dict card: card to set the values to
        :param int mana: total mana the values should be based on
        :returns:
            combined value of the attack and health generated
        '''

        #mana values for single attack and health points
        health_val = self.health_coeff
        attack_val = self.attack_coeff
        print("health val: " + str(health_val))
        print("attack val: " + str(attack_val))

        #random value between 0 and 1 using truncated normal distribution
        #with mean 0.5 and standard deviation 0.2
        rnd = truncnorm(-0.5/0.2, 0.5/0.2, loc=0.5, scale=0.2).rvs()

        health_val_target = rnd * mana
        attack_val_target = (1 - rnd) * mana

        card['health'] = int(round(health_val_target/health_val))
        card['attack'] = int(round(attack_val_target/attack_val))

        return card['health'] * health_val + card['attack'] * attack_val


def main():
    print("Test")
    creator = Cretor_agent()
    card = creator.create_card()
    print(card)


if __name__ == "__main__":
    main()
