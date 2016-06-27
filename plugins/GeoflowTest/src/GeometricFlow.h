///  @file GeometricFlow.h
///  @author  Elizabeth Jurrus, Andrew Stevens 
///  @brief main class for all Geometric Flow methods 
///  @ingroup Geoflow
///  @version $Id$
///  @attention
///  @verbatim
///
/// APBS -- Adaptive Poisson-Boltzmann Solver
///
///  Nathan A. Baker (nathan.baker@pnnl.gov)
///  Pacific Northwest National Laboratory
///
///  Additional contributing authors listed in the code documentation.
///
/// Copyright (c) 2010-2015 Battelle Memorial Institute. Developed at the
/// Pacific Northwest National Laboratory, operated by Battelle Memorial
/// Institute, Pacific Northwest Division for the U.S. Department of Energy.
///
/// Portions Copyright (c) 2002-2010, Washington University in St. Louis.
/// Portions Copyright (c) 2002-2010, Nathan A. Baker.
/// Portions Copyright (c) 1999-2002, The Regents of the University of
/// California.
/// Portions Copyright (c) 1995, Michael Holst.
/// All rights reserved.
///
/// Redistribution and use in source and binary forms, with or without
/// modification, are permitted provided that the following conditions are met:
///
/// Redistributions of source code must retain the above copyright notice, this
/// list of conditions and the following disclaimer.
///
/// Redistributions in binary form must reproduce the above copyright notice,
/// this list of conditions and the following disclaimer in the documentation
/// and/or other materials provided with the distribution.
///
/// Neither the name of the developer nor the names of its contributors may be
/// used to endorse or promote products derived from this software without
/// specific prior written permission.
///
/// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
/// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
/// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
/// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
/// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
/// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
/// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
/// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
/// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
/// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
/// THE POSSIBILITY OF SUCH DAMAGE.
///
/// @endverbatim
#ifndef __GeometricFlow_h_
#define __GeometricFlow_h_

#include <iostream>
#include <fstream>
#include <ostream>
#include <vector>
#include <map>
#include <iterator>
#include <sstream>
#include <algorithm>
#include <climits>
#include <stdio.h>
#include <valarray>

#include "Atom.h"
#include "Mat.h"
#include "ComData.h"
#include "GeometricFlowStruct.h"

#include <Eigen/Sparse>


using namespace std;


class GeometricFlow : protected GeometricFlowInput
{
   private:

      //
      //  Input Parameters - see .cpp for available documentation on these
      //  variables.
      //
      double p_expervalue;
      int    p_npiter;
      int    p_ngiter;
      double p_tauval;
      double p_prob;
      int    p_ffmodel;
      double p_sigmas;
      double p_epsilonw;
      double p_extvalue;
      int    p_iadi;
      double p_alpha;
      double p_tottf;
      int    p_maxstep;
      int    p_radexp;
      double p_holst_energy_unit;

      ComData p_comdata;

      int p_lj_iosetar;
      int p_lj_iosetaa;
      int p_lj_iwca;


   public:

      // only one boundary condition (BCFL_MDH) is actually implemented, so this
      // method doesn't change anything, documented for future updates in
      // github.
      void setBoundaryCondition( BoundaryType type ) { m_boundaryCondition = type; }

   private:


      // set up all the default variables
      void setupDefaults();  

      double left(const valarray<double>& pr, double h, double ev)
      {
         return floor( (pr - ev).min()/h ) * h - ev;
      }

      double right(const valarray<double>& pr, double h, double ev)
      {
         return ceil( (pr + ev).max()/h ) * h + ev;
      }

      double dot (double x, double y, double z) { return x*x + y*y + z*z; }


      void domainInitialization( const AtomList& atomlist );

      void yhsurface( const AtomList& atomList, 
         double tott, double dt, Mat<>& phitotx, Mat<>& surfu, int iloop,
         double& area, double& volume, double& attint, double alpha, int iadi,
         int igfin, double roro, double conms );

      void potIntegral(double rcfactor, size_t natm,
            valarray<double>& atom_x, valarray<double>& atom_y,
            valarray<double>& atom_z, valarray<double>& seta12,
            valarray<double>& seta6, valarray<double>& epsilon,
            valarray<double>& sigma, Mat<>& g, Mat<>& potr, Mat<>& pota);
      
      double volumeIntegration(const Mat<>& f);

      void upwinding(double dt, int nt, 
                              Mat<>& g, Mat<>& su, Mat<>& phitotx);

      void initial(double xl, double yl, double zl, int n_atom,
            const std::valarray<double>& atom_x, const std::valarray<double>& atom_y,
            const std::valarray<double>& atom_z, const std::valarray<double>& atom_r,
            Mat<>& g, Mat<>& phi);

      void normalizeSurfuAndEps (Mat<>& surfu, Mat<>& eps);

      void computeSoleng(double& soleng, 
                   Mat<>& phi, Mat<>& charget, Mat<size_t>& loc_qt);

      void seteqb( Mat<>& bg, const AtomList& al, const Mat<>& charget,
            const Mat<>& corlocqt);

      double qb(size_t i,size_t j,size_t k, const AtomList& al,
            const Mat<>& charget, const Mat<>& corlocqt );
      
      double qbboundary( double x, double y, double z, const AtomList& al );
      
      double qbinterior(double x, double y, double z, 
            const Mat<>& charget, const Mat<>& corlocqt);

      void pbsolver(const Mat<>& eps, Mat<>& phi, const Mat<>& bgf, double tol, int iter);

   public:

      //
      //  empty constructor
      //  (initialize with default parameters)
      GeometricFlow( );
      //  (initialize from struct)
      GeometricFlow( const struct GeometricFlowInput& gfi );
     
      friend struct GeometricFlowInput getGeometricFlowParams();

      //
      //  copy constructor
      // 
      GeometricFlow( const GeometricFlow& gf ) ;
      GeometricFlow( const GeometricFlow* gf ) ;

      //
      //  operator=
      //
      //GeometricFlow& operator=( const GeometricFlow& gf ) ;

      //
      //  Set and Get methods
      //
      void setExperValue( double exper_val ) { p_expervalue = exper_val; }

      void setPressure( double pres_i ) { m_press = pres_i; }
      
      void setGamma( double gamma ) { m_gamma = gamma; }
      
      void setFFModel( int ffmodel ) { p_ffmodel = ffmodel; }

      void setVDWDispersion( int vdwdispersion ) 
            { m_vdwdispersion = vdwdispersion; }

      void setExtValue( double extvalue ) { p_extvalue = extvalue; }
      
      void setSDie( double epsilons ) { m_sdie = epsilons; }
      
      void setPDie( double epsilonp ) { m_pdie = epsilonp; }

      void setGrid( double grid[3] ) 
         { m_grid[0] = grid[0];
           m_grid[1] = grid[1];
           m_grid[2] = grid[2]; }

      void setETolSolvation( double etol ) { m_etolSolvation = etol ; }

      void setETolSolver( double tol ) { m_tol = tol ; }
   
      //Lennard-Jones well depth parameter for water
      void setLJWell( double depth ) { p_epsilonw = depth ; } 

      // uncomment if needed:
      //void setNPiter( int npiter ) { p_npiter = npiter; }
      //void setNGiter( int ngiter ) { p_ngiter = ngiter; }
      //void setTauVal( double tauval ) { p_tauval = p_tauval; }
      //void setProb( double prob ) { p_prob = prob; }

      double getExperValue() { return p_expervalue; }

      double getPressure() { return m_press; }
      
      double getGamma() { return m_gamma; }
      
      int getFFModel() { return p_ffmodel; }

      double getVDWDispersion() { return m_vdwdispersion; }

      double getExtValue() { return p_extvalue; }
      
      double getSDie() { return m_sdie; }
      
      double getPDie() { return m_pdie; }

      double getRadExp() { return p_radexp; }

      //double& getGrid() { return m_grid; }

      void write() const ;

      //
      //  for debugging
      //
      void printAllParams();

      struct GeometricFlowOutput run( const AtomList& atomList );
      


};

#endif

      

