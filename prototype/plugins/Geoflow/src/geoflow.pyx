cimport cpbconcz2
from cython.view cimport array as cvarray

cdef double _get_pres_step(double pres):
	if pres < 0.001:
		return 0.0001
	elif pres < 0.01:
		return 0.001
	else:
		return 0.005

cdef double _get_gama_step(double gama):
	if gama < 0.0001:
		return 0.00001
	elif gama < 0.001:
		return 0.0001
	elif gama < 0.01:
		return 0.001
	else:
		return 0.005

cdef class Geoflow:
	cdef double _pres_i
	cdef double _gama_i
	cdef int _npiter
	cdef int _ngiter
	cdef double _tauval
	cdef double _prob
	cdef int _ffmodel  # 1 for ZAP-9/AM1-BCCv1; 2 for OPLS/AA
	cdef double _sigmas  # Angstrom (radius of water molecule based on LJ
	                     # parameter sigma)
	cdef double _epsilonw  # epsilon parameter of 0 (kcal/mol) of water molecule
	cdef int _vdwdispersion  # 1(on) or 0(off)- previously called REPULSIVE
	cdef double _extvalue  # (distance atom surface and box boundary)
	cdef int _iadi  # 0 for explicit scheme; 1 for ADI scheme
	cdef double _alpha  # weight of previous solution to change the next
	                    # solution in geometry flow
	cdef double _tol
	cdef double _tottf  # total time
	cdef double _dcel  # This is the grid spacing.
	cdef int _maxstep
	cdef double _epsilons
	cdef double _epsilonp
	cdef int _radexp
	cdef double _crevalue
	cdef double _density  # (use 0.03346)

	def __cinit__(self):
		self._pres_i = 0
		self._gama_i = 0
		self._npiter = 0
		self._ngiter = 0
		self._tauval = 0
		self._prob = 0
		self._ffmodel = 0
		self._sigmas = 0
		self._epsilonw = 0
		self._vdwdispersion = 0
		self._extvalue = 0
		self._iadi = 0
		self._alpha = 0
		self._tol = 0
		self._tottf = 0
		self._dcel = 0
		self._maxstep = 0
		self._epsilons = 0
		self._epsilonp = 0
		self._radexp = 0
		self._crevalue = 0
		self._density = 0

	def __init__(self, pres_i, gama_i, npiter, ngiter, tauval, prob, ffmodel,
			sigmas, epsilonw, vdwdispersion, extvalue, iadi, alpha, tol, tottf,
			dcel, maxstep, epsilons, epsilonp, radexp, crevalue, density):
		self._pres_i = pres_i
		self._gama_i = gama_i
		self._npiter = npiter
		self._ngiter = ngiter
		self._tauval = tauval
		self._prob = prob
		self._ffmodel = ffmodel
		self._sigmas = sigmas
		self._epsilonw = epsilonw
		self._vdwdispersion = vdwdispersion
		self._extvalue = extvalue
		self._iadi = iadi
		self._alpha = alpha
		self._tol = tol
		self._tottf = tottf
		self._dcel = dcel
		self._maxstep = maxstep
		self._epsilons = epsilons
		self._epsilonp = epsilonp
		self._radexp = radexp
		self._crevalue = crevalue
		self._density = density

	cdef _process_molecule(self, molecule, int igfin, double tpb, int iterf,
			int itert, double pres, double gama):
		cdef int natm, i
		cdef double[:, :] xyzr
		cdef double[:] pqr, ljepsilon
		cdef double dcel3[3]
		cdef cpbconcz2.GeoflowInput gfin
		cdef cpbconcz2.GeoflowOutput gfout

		natm = len(molecule['atoms'])
		xyzr = cvarray(shape=(natm, cpbconcz2.XYZRWIDTH),
				itemsize=sizeof(double), format="d")
		pqr = cvarray(shape=(natm,), itemsize=sizeof(double), format="d")
		ljepsilon = cvarray(shape=(natm,), itemsize=sizeof(double), format="d")

		for i, atom in enumerate(molecule['atoms']):
			xyzr[i, 0] = atom['pos'][0]
			xyzr[i, 1] = atom['pos'][1]
			xyzr[i, 2] = atom['pos'][2]
			xyzr[i, 3] = atom['radius'] * self._radexp
			pqr[i] = atom['charge']
			ljepsilon[i] = atom['ljepsilon'] if self._ffmodel != 1 else 0

		dcel3[:] = [self._dcel, self._dcel, self._dcel]
		gfin.dcel = dcel3;
		gfin.ffmodel = self._ffmodel;
		gfin.extvalue = self._extvalue;
		gfin.pqr = &pqr[0];
		gfin.maxstep = self._maxstep;
		gfin.crevalue = self._crevalue;
		gfin.iadi = self._iadi;
		gfin.tottf = self._tottf;
		gfin.ljepsilon = &ljepsilon[0];
		gfin.alpha = self._alpha;
		gfin.igfin = igfin;
		gfin.epsilons = self._epsilons;
		gfin.epsilonp = self._epsilonp;
		gfin.idacsl = 0;
		gfin.tol = self._tol;
		gfin.iterf = iterf;
		gfin.tpb = tpb;
		gfin.itert = itert;
		gfin.pres = pres;
		gfin.gama = gama;
		gfin.tauval = self._tauval;
		gfin.prob = self._prob;
		gfin.vdwdispersion = self._vdwdispersion;
		gfin.sigmas = self._sigmas;
		gfin.density = self._density;
		gfin.epsilonw = self._epsilonw;

		gfout = cpbconcz2.geoflowSolvation(
				<double (*)[cpbconcz2.XYZRWIDTH]> &xyzr[0,0], natm, gfin)

		return {'total': gfout.totalSolvation,
				'nonpolar': gfout.nonpolarSolvation,
				'elec': gfout.elecSolvation}

	def process_molecule(self, molecule):
		cdef double pres, pres_step, gama, gama_step, tpb
		cdef int indpres, indgama, igfin, iterf, itert
		
		results = []

		pres = self._pres_i

		for indpres in range(self._npiter):
			pres_step = _get_pres_step(pres)
			if indpres > 0:
				pres += pres_step

			gama = self._gama_i
			for indgama in range(self._ngiter):
				gama_step = _get_gama_step(gama)
				if indgama > 0:
					gama += gama_step

			igfin = 1
			tpb = 0.0
			iterf = 0
			itert = 0

			results.append(self._process_molecule(molecule, igfin, tpb, iterf,
					itert, pres, gama))

		return results
