from matplotlib import pyplot as plt
#import numpy as np
import snp2lib
from os import sep

# get the static dump dict and make the quests, modules, and assets easy to access
sdd = snp2lib.getSDdict()
quests = sdd['hunts']
modules = sdd['modules']
assets = sdd['assets']

# the base name is the overall folder, in it will be a folder for each set of banners, in those folders is where the
# graphs are saved
baseSaveFolderName = 'questGraphs'
baseSaveFolder = baseSaveFolderName + sep

# the plain static dump has the quest values for each customer, so get that and put them into a list
plainSD = snp2lib.getPlainSD()
clvs = plainSD['result']['customer_level_values']

# here's the range of levels, gear values and step size, and banners to check and graph
levelRange = range(1,22)
maxGearVal = int(7.5e6)
gearStep = int(1e3)
priceRange = range(0, maxGearVal, gearStep)
# the banner values aren't retrieved from the SD, so putting this higher than 6 will result in nonsense banner values
bannerRange = range(6)

# this sorts the quest IDs so they actually show up in order
qids = sorted([int(x) for x in quests])

# set the graph limits here
# 200 to 350 xp/hr shows the portion of the graphs you (probably) really want to see
graphsYlim = [200, 350]

# these are the xp and loot bonuses from the banners
# I suppose I could get them from the SD, but they're stored in a strange way and I don't really want to bother
grandBannerXPs = [0] + range(25, 46, 5)
grandBannerLoots = [0., 8.5, 9.5, 10.5, 11.5, 12.5]
classBannerXPs = [0, 6, 15, 30, 60, 90]
classBannerLoots = [0., 3., 6., 9., 12., 15.]

#'''
# for each banner level (3 GBs at bnLvl + 3 class banners at 3*bnLvl [since there are 15 total class banner levels]):
for bnLvl in bannerRange:
    # calc the xp and loot bonuses
    xpBonus = 3 * (grandBannerXPs[bnLvl] + classBannerXPs[bnLvl])
    comBonus = 3*(grandBannerLoots[bnLvl]/100. + classBannerLoots[bnLvl]/100.)
    uncBonus = 3*(grandBannerLoots[bnLvl]/200. + classBannerLoots[bnLvl]/200.)
    rareBonus = 3*(grandBannerLoots[bnLvl]/1000. + classBannerLoots[bnLvl]/1000.)
    # set the save folder name
    saveFolder = baseSaveFolder + 'banner_levels_{}'.format(bnLvl) + sep
    # for each customer level:
    for custLevel in levelRange:
        questPointSets = {}
        # lookup customer value for the quest
        custValue = clvs[custLevel]
        # for each quest:
        for x in qids:
            q = quests[str(x)]
            # as long as they can get xp for the quest:
            if custLevel <= q['max_level']:
                # get the quest name
                qname = assets[str(q['name_id'])]['value']
                xpphList = []
                # set the loot requirements
                commonReq = q['max_value'] / 10
                uncommonReq = commonReq / 0.15
                rareReq = commonReq / 0.025
                # xp per loot
                xppl = q['customer_xp_reward']
                # time
                qHours = q['duration'] / (60. * 60)
                # for each gear value:
                for gearValue in priceRange:
                    # set the actual chance of getting each look
                    comCh = min(gearValue/float(commonReq) + comBonus, 1)
                    uncCh = min(gearValue/float(uncommonReq) + uncBonus, 1)
                    rareCh = min(gearValue/float(rareReq) + rareBonus, 1)
                    # add it up, times the xp/loot, plus banner bonus
                    expectedXP = xppl * (comCh + uncCh + rareCh) + xpBonus
                    # calc xp/hr and append to the list
                    xpph = expectedXP/float(qHours)
                    xpphList.append(xpph)
                # store the list for each quest in a dict
                questPointSets[qname] = xpphList
        # then graph each quest
        fig, ax = plt.subplots()
        for y in questPointSets:
            # the gear values are in priceRange and the xp/hr values are in the dict
            ax.plot(priceRange, questPointSets[y])
            # each title is the customer level
            ax.set_title('level ' + str(custLevel))
            # only show the xp/hr region that's interesting (set earlier)
            ax.set_ylim(graphsYlim)
            ax.set_ylabel('xp per hour')
            ax.set_xlabel('gold in gear value')
            # add text for each quest line; this isn't perfect as they tend to overlap
            ax.text(priceRange[-1]+90000, questPointSets[y][-1], y, fontsize=6)
        # save each figure and close it so matplotlib doens't complain (and like memory leakage or whatever, blah blah)
        fig.savefig(saveFolder + 'level' + str(custLevel) + '.pdf')
        plt.close(fig)
print 'saved figures for levels {} to {}, in folder {}'.format(levelRange[0], levelRange[-1], baseSaveFolderName)
#'''
