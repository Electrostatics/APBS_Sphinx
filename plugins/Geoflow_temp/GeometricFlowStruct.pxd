cdef extern from "GeometricFlowStruct.h":

  ctypedef struct GeometricFlowInput:

  enum BoundaryType m_boundaryCondition:
  int m_vdwdispersion;
  double m_gamma;
  double m_grid[3];
  double m_etolSolvation;
  double m_tol;
  double m_pdie;
  double m_sdie;
  double m_press;
  double m_bconc;


  ctypedef struct GeometricFlowOutput:

	double m_area;
	double m_volume;
	double m_attint;
	double m_sumpot;
	double m_totalSolvation;
	double m_nonpolarSolvation;
	double m_elecSolvation;
