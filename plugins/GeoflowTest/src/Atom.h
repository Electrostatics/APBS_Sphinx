///  @file Atom.h
///  @author  Elizabeth Jurrus
///  @brief container class for atom information
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
#ifndef __Atom_h_
#define __Atom_h_

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

#include "Mat.h"
#include "ComData.h"

using namespace std;

class Atom
{
   private:

      double p_x, p_y, p_z;
      double p_radius;
      double p_pqr;
      double p_ljepsilon;

      void setRadius( const int ffmodel, double r )
      {
         if (ffmodel == 1 )
            p_radius = ( r < 1e-6 ) ? 1.21 : r;
         else
            p_radius = r;
      }

   public:

      //
      //  empty constructor
      //
      Atom( );
      Atom( const int ffmodel, double x, double y, double z, double r, double pqr);
      Atom( const int ffmodel, double x, double y, double z, double r, double pqr, double e );
      //~Path() { };

      //
      //  copy constructor
      //
      Atom( const Atom& A ) ;
      Atom( const Atom* A ) ;

      //
      //  operator=
      //
      //Atom& operator=( const Atom& A ) ;
      //ostream& operator<<( ostream& os, const Atom& A );

      double x() const { return p_x; }
      double y() const { return p_y; }
      double z() const { return p_z; }
      double r() const { return p_radius; }
      double pqr() const { return p_pqr; }
      double epsilon() const { return p_ljepsilon; }

      //
      //  for debugging
      //
      void print() const;
};

class AtomList
{
   private:

      vector< Atom > p_atomList;

   public:

      AtomList();

      AtomList( string xyzr_file, const double radexp, const int ffmodel );

      //AtomList( double* xyzrs, double* pqrs, const int num_atoms, const double radexp, const int ffmodel );

      AtomList( const AtomList& AL ) { p_atomList = AL.p_atomList ; }

      AtomList( const AtomList* AL ) { p_atomList = AL->p_atomList ; }

      unsigned int size() const { return p_atomList.size(); }

      const Atom& get( unsigned int i ) const { return p_atomList[i]; }

      void add( Atom A ) { p_atomList.push_back(A); };

      void changeChargeDistribution
         ( Mat<>& charget, Mat<>& corlocqt, Mat< size_t>& loc_qt,
           const ComData& comData ) const;

      void print() const;
};

#endif
