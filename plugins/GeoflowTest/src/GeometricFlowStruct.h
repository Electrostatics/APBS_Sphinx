#ifndef __GEOMETRICFLOWSTRUCT_H
#define __GEOMETRICFLOWSTRUCT_H

// Boundary element type
// TODO: "focus" (higher priority) and "sdh" should be added;  Only type
// implemented is MDH
//enum BoundaryType{ ZERO, SDH, MDH, FOCUS, MAP};
// these boundary types are copied from vhal.h in the apbs source
enum BoundaryType{

    ZERO=0,  /**< Zero Dirichlet boundary conditions */
    SDH=1,  /**< Single-sphere Debye-Huckel Dirichlet boundary
             * condition */
    MDH=2,  /**< Multiple-sphere Debye-Huckel Dirichlet boundary
             * condition */
    UNUSED=3,  /**< Unused boundary condition method (placeholder) */
    FOCUS=4,  /**< Focusing Dirichlet boundary condition */
    MEM=5,  /**< Focusing membrane boundary condition */
    MAP=6    /**< Skip first level of focusing use an external map */
};

//
//  input
//
struct GeometricFlowInput {

  enum BoundaryType m_boundaryCondition;
  int m_vdwdispersion;  // 1/0, on/off 
  double m_gamma;
  double m_grid[3];
  double m_etolSolvation;
  double m_tol;
  double m_pdie;
  double m_sdie;
  double m_press;
  double m_bconc;

#ifdef __cplusplus
GeometricFlowInput() :
  // default boundary condition -- see seteqb for details
  m_boundaryCondition(MDH),

  // VDWDISPERSION:  1(on) or 0 (off)- previously called REPULSIVE.
  // This is the option to include the dispersion force between solvent
  // and solute molecules in non-polar contribution of solvation energy.
  // It is different from the surface definition (i.e., van der Waals
  // surface) which is critical to define the simulation domain)
    m_vdwdispersion(0),

    m_gamma(0.0001),

  // grid spacing; distance per cell
    m_grid{0.25, 0.25, 0.25},

  // error tolerance for th esolvation difference values.  Formerly CREVALUE
  // in the Fortran and C code.
    m_etolSolvation(0.01),

  // Tolerance for the Eigen pbsolver
    m_tol(1e-4),

  // Solute dielectric
    m_pdie(1.5),

  // Solvent dielectric, from Thomas et. al.
    m_sdie(80),

    m_press(0.008),

  // Bulk solvent density from Thomas et. al.
    m_bconc(0.03347)
	   {}
#endif

} ;

//
//  output
//
struct GeometricFlowOutput {

	double m_area,
		m_volume,
		m_attint,
		m_sumpot,
		m_totalSolvation,
		m_nonpolarSolvation,
		m_elecSolvation;

} ;

#endif
