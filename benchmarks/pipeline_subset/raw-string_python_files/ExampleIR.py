
from Ramacropy.Ramacropy import IRSpectra as Spec

StarchA = Spec('./DataFiles/20230301/StarchA.txt')
StarchB = Spec('./DataFiles/20230301/StarchB.txt')
StarchC = Spec('./DataFiles/20230301/StarchC.txt')
Starch_00 = Spec('./DataFiles/20230301/starch_00.txt')
Starch_85 = Spec('./DataFiles/20230301/starch_85.txt')

# StarchA.plot_few(other_spectra=[StarchB,StarchC,Starch_85,Starch_00])

StarchA.t_to_A()
StarchB.t_to_A()
StarchC.t_to_A()
Starch_00.t_to_A()
Starch_85.t_to_A()

StarchA.baseline(interactive = True)
StarchB.baseline(coarsness=0.3)
StarchC.baseline(coarsness=0.3)
Starch_00.baseline(coarsness=0.3)
Starch_85.baseline(coarsness=0.3)

StarchA.normalise_peak(peak_wn=1000)
StarchB.normalise_peak(peak_wn=1000)
StarchC.normalise_peak(peak_wn=1000)
Starch_00.normalise_peak(peak_wn=1000)
Starch_85.normalise_peak(peak_wn=1000)

# StarchA.plot_few(other_spectra=[StarchB,StarchC,Starch_85,Starch_00])

StarchA.spec_pos_val(position = 1728)
StarchB.spec_pos_val(position = 1728)
StarchC.spec_pos_val(position = 1728)
Starch_00.spec_pos_val(position = 1728)
Starch_85.spec_pos_val(position = 1728)

StarchA.plot_calibration(acetyl_85=Starch_85,acetyl_0=Starch_00,starch_b=StarchB,starch_c=StarchC)

