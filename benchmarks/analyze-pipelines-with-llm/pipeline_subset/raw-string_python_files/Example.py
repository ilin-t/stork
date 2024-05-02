#import package
from Ramacropy.Ramacropy import RamanSpectra as Spectra
# load data
Spec1 = Spectra('DataFiles/20230301/Example_Processed_after.csv')
Spec2 = Spectra('DataFiles/20230301/Raman_test3.asc')

# baselien correct
# Spec1.baseline(interactive=True)
# Spec2.baseline(interactive=True)

#normalise
Spec1.normalise(method = 'area', interactive=True)
Spec2.normalise(method = 'area', interactive=True)

# integrate
Spec1.integrate(interactive=True)
Spec2.integrate(interactive=True)
# plot
Spec1.plot_integral_single(other_spectra=[Spec2], labels=['After','Before'])
Spec1.plot_few(other_spectra=[Spec2], labels=['After','Before'])
# save
# Spec1.save_changes()
# Spec2.save_changes(filename='Example_Processed_after.csv')