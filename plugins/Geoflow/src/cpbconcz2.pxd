cdef extern from "cpbconcz2.h":
	# Four because: 0-2 => pos, 3 => radius
	cdef enum:
		XYZRWIDTH = 4

	ctypedef struct GeoflowOutput:
		double area
		double volume
		double attint
		double sumpot
		double totalSolvation
		double nonpolarSolvation
		double elecSolvation

	ctypedef struct GeoflowInput:
		double* dcel;
		int ffmodel;
		double extvalue;
		double* pqr;
		int maxstep;
		double crevalue;
		int iadi;
		double tottf;
		double* ljepsilon;
		double alpha;
		int igfin;
		double epsilons;
		double epsilonp;
		int idacsl;
		double tol;
		int iterf;
		double tpb;
		int itert;
		double pres;
		double gama;
		double tauval;
		double prob;
		int vdwdispersion;
		double sigmas;
		double density;
		double epsilonw;

	GeoflowOutput geoflowSolvation(double xyzr[][XYZRWIDTH], size_t natm,
			GeoflowInput gfin);

