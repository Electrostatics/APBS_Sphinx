///  @file Atom.cpp
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
#include "Atom.h"

#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string.hpp>
#include <valarray>

using namespace std;

Atom::Atom( )
{
   p_x = 0;
   p_y = 0;
   p_z = 0;
   p_radius = 0;
   p_pqr = 0;
   p_ljepsilon = 0;
}
Atom::Atom( const int ffmodel, double x, double y, double z, double r, double pqr)
{
   p_x = x;
   p_y = y;
   p_z = z;

   setRadius( ffmodel, r );

   p_pqr = pqr;
}

Atom::Atom( const int ffmodel, double x, double y, double z, double r, double pqr, double e)
{
   p_x = x;
   p_y = y;
   p_z = z;

   setRadius( ffmodel, r );

   p_pqr = pqr;
   p_ljepsilon = e;
}

//~Atom() { };

//
//  copy constructor
//
Atom::Atom( const Atom& A )
{
   p_x = A.p_x;
   p_y = A.p_y;
   p_z = A.p_z;
   p_radius = A.p_radius;
   p_pqr = A.p_pqr;
   p_ljepsilon = A.p_ljepsilon;
}

Atom::Atom( const Atom* A )
{
   p_x = A->p_x;
   p_y = A->p_y;
   p_z = A->p_z;
   p_radius = A->p_radius;
   p_pqr = A->p_pqr;
   p_ljepsilon = A->p_ljepsilon;
}

//
//  operator=
//
//Atom& Atom::operator=( const Atom& gf )
//{
//}

/*ostream& Atom::operator<<(std::ostream& os, const Atom& A)
{
   // os << A.p_x << ", " << A.p_y << ", " << A.p_z << ": " << A.p_radius << endl ;

   return os;
}
*/
void Atom::print() const
{
   cout << p_x << ", "
      << p_y << ", "
      << p_z << "; "
      << p_radius << ", "
      << p_pqr << ", "
      << p_ljepsilon << endl ;
}

AtomList::AtomList() { }


AtomList::AtomList( string xyzr_file, const double radexp, const int ffmodel )
{
   std::ifstream f;
   f.open( xyzr_file.c_str() );
   if( f  )
   {
      //   std::fill(ljepsilon, ljepsilon + MAXATOMS, 0.0);

      string line;
      while (getline(f, line) ) // !f.eof() )
      {
         //cout << "line: " << line << endl;
         // tokenize the string
         vector< string > one_line;  // split with tabs or spaces
         boost::split(one_line, line, boost::is_any_of("\t "), boost::token_compress_on);
         if ( one_line.size() > 5)
         {
            // reading in x, y, z, r, pqr, ljepsilon (ignoring the rest of
            // the file
            Atom A( ffmodel,
                  stod(one_line[0]), stod(one_line[1]), stod(one_line[2]),
                  stod(one_line[3]) * radexp,
                  stod(one_line[4]),
                  stod(one_line[5]) );
            p_atomList.push_back( A );
         }
         else
         {
            // reading in x, y, z, r, pqr
            Atom A( ffmodel,
                  stod(one_line[0]), stod(one_line[1]), stod(one_line[2]),
                  stod(one_line[3]) * radexp,
                  stod(one_line[4]) );
            p_atomList.push_back( A );
         }
      }
   }
   else
   {
      cout << "ERROR: Can't read " << xyzr_file << endl ;
      exit(1);
   }
   f.close();

}

/*
AtomList::AtomList( double* xyzrs, double* pqrs, const int num_atoms,
                    const double radexp, const int ffmodel )
{
   for( unsigned int an; an < num_atoms; an++ )
   {
      Atom A( ffmodel,
            xyzrs[an][0], xyzrs[an][1], xyzrs[an][2],
            xyzrs[an][3] * radexp,
            pqrs[an] );
      p_atomList.push_back( A );

    }
}
*/

/*
 * change the charge distribution for each atom:
 *
 * - xyzr contains the position and radius of each atom in the molecule.  Each
 *   atom's position (x,y,z) is stored in the first three elements and it's
 *   radius as the fourth element.
 * - chratm is an array that contains the charge of each atom indexed by atom as
 *    xyzr.  Note that this is called pqr in other parts of the code.
 * - charget is a matrix of size (natm, 8)
 * - corlocqt is a matrix of size (natm, 8, 3)
 * - loc_qt is a matrix of size (natm, 8, 3)
 * - iatm is the index of the atom for which we want the charge distribution
 *   calculated.
 */
void AtomList::changeChargeDistribution
      ( Mat<>& charget, Mat<>& corlocqt, Mat< size_t>& loc_qt,
        const ComData& comdata ) const
{
	//for (size_t iatm = 1; iatm <= natm; iatm++) {
	//	chargedist(xyzr, pqr, charget, corlocqt, loc_qt, iatm);
	//}

   for( unsigned int iatm = 1; iatm <= p_atomList.size(); iatm++ )
   {
      double x_q = p_atomList[ iatm-1 ].x(); //xyzr[iatm-1][0];
      double y_q = p_atomList[ iatm-1 ].y(); //xyzr[iatm-1][1];
      double z_q = p_atomList[ iatm-1 ].z(); //xyzr[iatm-1][2];
      double q_q = p_atomList[ iatm-1 ].pqr(); //chratm[iatm-1];

      size_t i_q = comdata.inverx(x_q);
      int j_q = comdata.invery(y_q);
      int k_q = comdata.inverz(z_q);

      // std::cout << x_q << "," << y_q << "," << z_q << " " << i_q << "," << j_q
      // 	<< "," << k_q << std::endl;


      Mat<size_t> loc_q(8,3);
      Mat<> corlocq(8,3);
      for (size_t i = 0; i <= 1; ++i) {
         for (size_t j = 0; j <= 1; ++j) {
            for (size_t k = 0; k <= 1; ++k) {
               size_t ind = 4*k + 2*j + i + 1;

               size_t ind_i = i_q + i;
               size_t ind_j = j_q + j;
               size_t ind_k = k_q + k;

               corlocq(ind,1) = comdata.xvalue(ind_i);
               corlocq(ind,2) = comdata.yvalue(ind_j);
               corlocq(ind,3) = comdata.zvalue(ind_k);
               // std::cout << "ind: " << ind << std::endl;
               // std::cout << "corlocq" << std::endl
               // 	<< corlocq(ind, 1) << ","
               // 	<< corlocq(ind, 2) << ","
               // 	<< corlocq(ind, 3) << std::endl;

               loc_q(ind,1) = ind_i;
               loc_q(ind,2) = ind_j;
               loc_q(ind,3) = ind_k;
               // std::cout << "loc_q" << std::endl
               // 	<< loc_q(ind, 1) << ","
               // 	<< loc_q(ind, 2) << ","
               // 	<< loc_q(ind, 3) << std::endl;
            }
         }
      }


      double x = comdata.xvalue(i_q);
      double y = comdata.yvalue(j_q);
      double z = comdata.zvalue(k_q);

      double xd1 = x_q - x;
      double yd1 = y_q - y;
      double zd1 = z_q - z;

      valarray<double> charge(0.0, 8);
      if (xd1 != 0 && yd1 != 0 && zd1 != 0) {
         for (int i = 0; i <= 1; ++i) {
            for (int j = 0; j <= 1; ++j) {
               for (int k = 0; k <= 1; ++k) {
                  int ind = 4*k + 2*j + i;

                  double xd = i*comdata.deltax() - xd1;
                  double yd = j*comdata.deltay() - yd1;
                  double zd = k*comdata.deltaz() - zd1;

                  charge[ind] = 1.0/fabs(xd*yd*zd);
               }
            }
         }
      }
      else if ((xd1 != 0 && yd1 != 0) || (xd1 != 0 && zd1 != 0) ||
            (yd1 != 0 && zd1 != 0)) {
         if (xd1 == 0) {
            for (int j = 0; j <= 1; ++j) {
               for (int k = 0; k <= 1; ++k) {
                  double yd = j*comdata.deltay() - yd1;
                  double zd = k*comdata.deltaz() - zd1;
                  charge[4*j + 2*k] = 1.0/fabs(yd*zd);
               }
            }
         }
         else if (yd1 == 0) {
            for (int i = 0; i <= 1; ++i) {
               for (int k = 0; k <= 1; ++k) {
                  double xd = i*comdata.deltax() - xd1;
                  double zd = k*comdata.deltaz() - zd1;
                  charge[i + 4*k] = 1.0/fabs(xd*zd);
               }
            }
         }
         else if (zd1 == 0) {
            for (int i = 0; i <= 1; ++i){
               for (int j = 0; j <= 1; ++j){
                  double xd = i*comdata.deltax() - xd1;
                  double yd = j*comdata.deltay() - yd1;
                  charge[i + 2*j] = 1.0/fabs(xd*yd);
               }
            }
         }
      }
      else if (xd1 != 0 || yd1 != 0 || zd1 != 0 ) {
         if (xd1 != 0) {
            charge[0] = 1.0/xd1;
            charge[1] = 1.0/(comdata.deltax()-xd1);
         }
         else if (yd1 != 0) {
            charge[0] = 1.0/yd1;
            charge[2] = 1.0/(comdata.deltay()-yd1);
         }
         else if (zd1 != 0) {
            charge[0] = 1.0/zd1;
            charge[4] = 1.0/(comdata.deltaz()-zd1);
         }
      }
      else {
         charge[0] = 1.0;
      }

      charge = q_q*charge / charge.sum();

      for (size_t j = 1; j <= charget.ny(); ++j) {
         charget(iatm,j) = charge[j-1];
         for (size_t k = 1; k <= corlocqt.nz(); ++k) {
            corlocqt(iatm,j,k) = corlocq(j,k);
            loc_qt(iatm,j,k) = loc_q(j,k);

         }
      }

   }
}

void AtomList::print() const
{
   for(unsigned int i = 0; i < p_atomList.size(); i++)
      p_atomList[ i ].print();
}
