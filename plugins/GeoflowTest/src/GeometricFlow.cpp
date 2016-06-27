///  @file GeometricFlow.cpp
///  @author Elizabeth Jurrus, Andrew Stevens, Peter Hui, Kyle Monson, Zhan Chen, Guowei Wei
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
#include "GeometricFlow.h"
#include "Mat.h"

using namespace std;

GeometricFlow::GeometricFlow() : GeometricFlowInput()
{
  setupDefaults();  // initialize all the other stuff we don't want the
                    // interface to see
}

GeometricFlow::GeometricFlow(const struct GeometricFlowInput &gfi)
  : GeometricFlowInput(gfi) // Rely on default copy constructor
{
   setupDefaults();
}

//
//  setupDefaults - set up all the other defaults in the code we don't
//  want the "users" to see or mess with
//
void GeometricFlow::setupDefaults()
{
   p_npiter = 1;
   p_ngiter = 1;

   // probe radius for creating the solvent accessible surface
   p_tauval = 1.40;

   p_prob = 0.0;

   p_ffmodel = 1;  // FFMODEL: 1 for ZAP-9/AM1-BCCv1; 2 for OPLS/AA

   // Solvent radius (SIGMAS: Angstrom (radius of water molecule based 
   //   on LJ parameter sigma)
   p_sigmas = 1.5828; // from Thomas et al.

   // EPSILONW:  epsilon parameter of O (kcal/mol) of water molecule...
   // the Lennard-Jones well depth parameter for water.  Perhaps we could
   // call it ljwell?
   p_epsilonw = 0.1554; // from Thomas et al.

   
   // EXTVALUE:  (distance atom surface and box boundary)
   p_extvalue = 1.90;
   // iprec
   // IPREC: flag to indicate the usage of preconditioner iprec =1 (yes); 0 (no)
   // istep
   p_iadi = 0;

   // ALPHA: weight of previous solution to change the next solution in geometry flow
   p_alpha = 0.50;
   
   // IPBIN  //IPBIN: start guess for PB 1; inherit '0' - not used?
   p_tottf = 3.5;
   p_maxstep = 20;

   p_radexp = 1;

   // idacsl //idacsl: 0 for solvation force calculation; 1 or accuracy test

   
   p_comdata.init( m_grid );

   // http://ccom.ucsd.edu/~mholst/pubs/dist/Hols94d.pdf (see page 12)
   p_holst_energy_unit = 332.06364;

   p_lj_iosetar = 1;
   p_lj_iosetaa = 1;
   p_lj_iwca = 1;

}

//~GeometricFlow() { };

/*
//  TODO - need to implement?
//  copy constructor - constructors are commented out for maintenance.
// 
GeometricFlow::GeometricFlow( const GeometricFlow& gf )
{
}

GeometricFlow::GeometricFlow( const GeometricFlow* gf )
{
}
*/

//
//  operator=
//
//GeometricFlow& GeometricFlow::operator=( const GeometricFlow& gf )
//{
//}

void printAllParams()
{
}

//template class Mat<double>;
//template
//std::ostream& operator<< <double> ( std::ostream& os, const Mat<double>& M);

struct GeometricFlowOutput GeometricFlow::run( const AtomList& atomList )
{
   //
   //  initialize the domain - set up the grid size and length
   //
   domainInitialization( atomList );
	std::cout << "dimensions:\t" << p_comdata.nx() << " " <<
      p_comdata.ny() << " " << p_comdata.nz() << std::endl;
	std::cout << "grid spacing:\t" << p_comdata.deltax() << " " <<
      p_comdata.deltay() << " " << p_comdata.deltaz() << std::endl;

  
   //
   //  assign charge distributions
   //
   unsigned int natm = atomList.size();
   Mat<> charget(natm, 8);
	Mat<> corlocqt(natm, 8, 3);
	Mat<size_t> loc_qt(natm,8,3);
   atomList.changeChargeDistribution( charget, corlocqt, loc_qt, p_comdata );
   //atomList.print();
   //cout<< "test: " ; p_comdata.print(); cout << endl ;

   //
   //  setup phi
   //
	Mat<> phi( p_comdata.nx(), p_comdata.ny(), p_comdata.nz(),
              p_comdata.deltax(), p_comdata.deltay(), p_comdata.deltaz() ), 
         phix( phi ), 
         phivoc( phi ), 
         surfu( phi ), 
         eps( phi ),
			bg( phi );

   vector<double> solv(p_maxstep+1);  // keep track of the solvation energies
	double diffEnergy = 100;

	int iloop = 0; 
	double tott = 0.0;
	double elec = 0.0, area = 0.0, volume = 0.0, attint = 0.0;
   double tpb = 0.0;  // time step calculation for total pb
   int iterf = 0, itert = 0; // iteration num for first iteration and total
   double potcoe = 1.0 / m_gamma;
   double lj_roro = m_bconc / m_gamma;
   double lj_conms = m_press / m_gamma;
   int igfin = 1;
   //std::cout << "blahh: " << m_press << " " << m_gamma << std::endl;

   //
   // iteration coupling surface generation and poisson solver
   //
   while ( (iloop < p_maxstep) && (diffEnergy > m_etolSolvation) ) 
   {
      iloop++;
      double deltat = 0; //this is wrong for adi...
      if (!p_iadi) {
         deltat =
            pow(p_comdata.deltax()*p_comdata.deltay()*p_comdata.deltaz(), 2.0/3.0)/4.5;
      }
      //std::cout << "deltat = " << deltat << std::endl;

      double totnow = p_tottf - iloop + 1;
      if (totnow > 1.0) {
         tott = totnow;
      } else {
         tott = 1.0;
      }

		area = volume = attint = 0.0;
		yhsurface(atomList, tott, deltat, phix, surfu, iloop, area,
   			    volume, attint, p_alpha, p_iadi, igfin, lj_roro, lj_conms);
		normalizeSurfuAndEps(surfu, eps); 
      // Keith wants surfu printed into a dx file
      //cout << "surfu: " ; surfu.print(); std::cout << std::endl ;
      //cout << "eps: " ; eps.print(); std::cout << std::endl ;
      //cout << "charget: " ; charget.print(); std::cout << std::endl ;
      //cout << "corlocqt: " ; corlocqt.print(); std::cout << std::endl ;

      //
      // Create B (bg)
      // 
		if (iloop == 1) {
			seteqb(bg, atomList, charget, corlocqt );
		}

      //
      //  call the PB Solver!
      //
		int iter = 1000;
		double fpb, titer = 0.0;
		pbsolver(eps, phi, bg, m_tol, iter);
		if (iloop == 1) {
			fpb = titer;
			iterf = iter;
		}
		tpb = tpb + titer;
		itert += iter;

		eps = m_pdie;
		if (iloop == 1) {
			pbsolver(eps, phivoc, bg, m_tol, iter);
		}

		for (size_t ix = 2; ix <= p_comdata.nx() - 1; ix++) {
			for (size_t iy = 2; iy <= p_comdata.ny() - 1; iy++) {
				for (size_t iz = 2; iz <= p_comdata.nz() - 1; iz++) {
					double phixx = phi(ix+1,iy,iz) -
                  phi(ix-1,iy,iz)/(2.0*p_comdata.deltax());
					double phixy = phi(ix,iy+1,iz) -
                  phi(ix,iy-1,iz)/(2.0*p_comdata.deltay());
					double phixz = phi(ix,iy,iz+1) -
                  phi(ix,iy,iz-1)/(2.0*p_comdata.deltaz());

					phix(ix,iy,iz) = 0.5 * (m_sdie - m_pdie) * (phixx *
							phixx +	phixy * phixy + phixz * phixz) * potcoe;
				}
			}
		}

		// solvation
		cout << "iloop = " << iloop << std::endl;
		double soleng1, soleng2;
		soleng1 = soleng2 = 0.0;
      //cout << "phi: " ; phi.print(); cout << endl;
		computeSoleng(soleng1, phi, charget, loc_qt);
		computeSoleng(soleng2, phivoc, charget, loc_qt);
		std::cout << "soleng1 = " << soleng1 << std::endl;
		std::cout << "soleng2 = " << soleng2 << std::endl;
		//std::cout << "soleng2 is too small!!" << std::endl;  // why is this here?
		elec = (soleng1 - soleng2) * p_holst_energy_unit;
		solv[iloop - 1] = elec + m_gamma * (area + volume * lj_conms + attint *
				lj_roro);
		if (iloop > 1) {
			diffEnergy = fabs((solv[iloop - 1] - solv[iloop - 2]));
		}
      // print the solvation energies by loop index; want to only print
      // the last two energies???  this prints them all.
      for (int i = 0; i < iloop; i++ )
      {
         std::cout << "solv[" << i << "] = " << solv[i] << std::endl;
      }
		std::cout << "diffEnergy = " << diffEnergy << std::endl;
	}


   struct GeometricFlowOutput geoflowOut;

	double sumpot = area + volume * lj_conms + attint * lj_roro;
	geoflowOut.m_nonpolarSolvation = sumpot*m_gamma;
	geoflowOut.m_totalSolvation = geoflowOut.m_nonpolarSolvation + elec;
   geoflowOut.m_elecSolvation = elec;
   cout << "totalSolv:\t" << geoflowOut.m_totalSolvation << "\t";
   cout << "nonpolar: " << geoflowOut.m_nonpolarSolvation << "\t";
   cout << "electro: " << geoflowOut.m_elecSolvation << "\n" << std::endl;

   return geoflowOut;

}

//
//  Set up the grid - create a bounding box around the atoms, padded by
//  p_extvalue.
//
void GeometricFlow::domainInitialization( const AtomList& atomList )
{
   unsigned int natm = atomList.size();
    std::valarray<double> atom_x(natm), 
                          atom_y(natm),
                          atom_z(natm), 
                          atom_r(natm);

	for(size_t i = 0; i < natm; ++i) 
   {
		atom_x[i] = atomList.get(i).x(); 
		atom_y[i] = atomList.get(i).y(); 
		atom_z[i] = atomList.get(i).z(); 
		atom_r[i] = atomList.get(i).r(); 
	}

	double xleft = left(atom_x - atom_r, p_comdata.deltax(), p_extvalue);
	double yleft = left(atom_y - atom_r, p_comdata.deltay(), p_extvalue);
	double zleft = left(atom_z - atom_r, p_comdata.deltaz(), p_extvalue);

	double xright = right(atom_x + atom_r, p_comdata.deltax(), p_extvalue);
	double yright = right(atom_y + atom_r, p_comdata.deltay(), p_extvalue);
	double zright = right(atom_z + atom_r, p_comdata.deltaz(), p_extvalue);

	int nx = (xright - xleft)/p_comdata.deltax() + 1;
	int ny = (yright - yleft)/p_comdata.deltay() + 1;
	int nz = (zright - zleft)/p_comdata.deltaz() + 1;

	xright = xleft + p_comdata.deltax()*(nx - 1);
	yright = yleft + p_comdata.deltay()*(ny - 1);
	zright = zleft + p_comdata.deltaz()*(nz - 1);

	//keep this around for later
   p_comdata.setBounds( xleft, xright, 
                        yleft, yright,
                        zleft, zright,
                        nx, ny, nz );

}

//
//		yhsurface
//
void GeometricFlow::yhsurface( const AtomList& atomList,
		double tott, double dt, Mat<>& phitotx, Mat<>& surfu, int iloop,
		double& area, double& volume, double& attint, double alpha, int iadi,
		int igfin, double roro, double conms )
{
   const int natm = atomList.size();
	size_t nx = p_comdata.nx(), ny = p_comdata.ny(), nz = p_comdata.nz();
	double xl = p_comdata.xleft(), yl = p_comdata.yleft(), zl = p_comdata.zleft();
	std::valarray<double> atom_x(natm), atom_y(natm), atom_z(natm), atom_r(natm);
	for (size_t i = 0; i < natm; ++i) {
		atom_x[i] = atomList.get(i).x();
		atom_y[i] = atomList.get(i).y();
		atom_z[i] = atomList.get(i).z();
		atom_r[i] = atomList.get(i).r();
	}

	Mat<> su(surfu), g(surfu);
	initial(xl, yl, zl, natm, atom_x,atom_y, atom_z, atom_r, g, su);
	if (iloop > 1 && igfin == 1)
		su = surfu;
   //cout << "test2: " ; su.print(); cout << endl ;
   //cout << "test2: " ; g.print(); cout << endl ;

	double rcfactor = (p_ffmodel == 1) ? 1.0 : pow(2.0, 1.0/6.0);
	std::valarray<double> sigma(atom_r);
	std::valarray<double> seta12(natm), seta6(natm), epsilon(natm);

	if (p_ffmodel == 1) {
		for (size_t i = 0; i < natm; ++i) {
			sigma[i] = atom_r[i] + p_sigmas;
			if (m_vdwdispersion != 0) {
				double se = sigma[i]/(atom_r[i] + p_prob);
				epsilon[i] = pow( pow(se, 12.0) - 2.0*pow(se, 6.0) , -1.0);
			}
			seta12[i] = p_lj_iosetar * m_vdwdispersion * epsilon[i];
			seta6[i] = 2.0*p_lj_iosetaa * m_vdwdispersion * epsilon[i];
		}
	} else {
		for (size_t i = 0; i < natm; ++i) {
			sigma[i] = sqrt(4.0* atom_r[i] * p_sigmas);
			if (m_vdwdispersion != 0) {
				epsilon[i] = sqrt(atomList.get(i).epsilon() * p_epsilonw);
				seta12[i] = 4.0*epsilon[i];
				seta6[i] = 4.0*epsilon[i];
			}
		}
	}

	Mat<> potr(nx,ny,nz), pota(nx,ny,nz);
	potIntegral(rcfactor, natm, atom_x, atom_y, atom_z, seta12, seta6,
			epsilon, sigma, g, potr, pota);

	if (p_lj_iwca == 1)
		potr = 0;

   //cout << conms << " " << roro << endl ;
	for (size_t i = 0; i < phitotx.size(); ++i) {
		phitotx[i] = -conms - phitotx[i] + roro*(potr[i] + pota[i]);
	}
   //cout << "test2: " ; phitotx.print(); cout << endl ;

	if (iadi == 0 || iloop > 1) {
		int nt = ceil(tott/dt) + 1;
		upwinding(dt, nt, g, su, phitotx);
	} else {
		std::cerr << "ADI not implemented..." << std::endl;
		exit(1);
	}
   //cout << "test2: " ; su.print(); cout << endl ;

	if (iloop > 1) {
		for (size_t i = 0; i < surfu.size(); ++i) {
		   surfu[i] = surfu[i]*alpha + su[i]*(1.0 - alpha);
		}
		su = surfu;
	} else {
		surfu = su;
	}

//   cout << "alpha: " << alpha << endl;
//   cout << "test2: " ; su.print(); cout << endl ;

	volume = volumeIntegration(su);
	std::cout << "volume = " << volume << std::endl;

	Mat<> fintegr(nx,ny,nz);
	double dx = p_comdata.deltax(), dy = p_comdata.deltay(), dz = p_comdata.deltaz();
	for (size_t x = 2; x < nx; ++x) {
		for (size_t y = 2; y < ny; ++y) {
			for (size_t z = 2; z < nz; ++z) {
				double sux = su(x+1,y,z) - su(x-1,y,z);
				double suy = su(x,y+1,z) - su(x,y-1,z);
				double suz = su(x,y,z+1) - su(x,y,z-1);
				fintegr(x,y,z) = sqrt( dot(sux/(2.0*dx), suy/(2.0*dy), suz/(2.0*dz)));
			}
		}
	}

	area = volumeIntegration(fintegr);
	std::cout << "area = " << area << std::endl;

	potIntegral(rcfactor, natm, atom_x, atom_y, atom_z, seta12, seta6,
			epsilon, sigma, g, potr, pota);

	if (p_lj_iwca == 1) {
		for (size_t i = 0; i < fintegr.size(); ++i) {
			fintegr[i] = pota[i]*(1e3 - su[i]);
		}
	} else {
		for (size_t i = 0; i < fintegr.size(); ++i) {
			fintegr[i] = (pota[i] + potr[i])*(1e3 - su[i]);
		}
	}

	attint = volumeIntegration(fintegr);
	std::cout << "attint = " << attint << std::endl;
}


//
//  potIntegral
//
void GeometricFlow::potIntegral(double rcfactor, size_t natm,
      valarray<double>& atom_x, valarray<double>& atom_y,
      valarray<double>& atom_z, valarray<double>& seta12,
      valarray<double>& seta6, valarray<double>& epsilon,
      valarray<double>& sigma, Mat<>& g, Mat<>& potr, Mat<>& pota)
{
   double dx = p_comdata.deltax(), dy = p_comdata.deltay(), dz = p_comdata.deltaz();
   for (size_t x = 2; x < potr.nx(); ++x) {
      for (size_t y = 2; y < potr.ny(); ++y) {
         for (size_t z = 2; z < potr.nz(); ++z) {

            if (g(x,y,z) == 0) { continue; }

            double pr=0, pa=0;
            for (size_t a = 0; a < natm; ++a) {
               const double xi = p_comdata.xleft() + (x-1)*dx;
               const double yi = p_comdata.yleft() + (y-1)*dy;
               const double zi = p_comdata.zleft() + (z-1)*dz;
               const double dist = sqrt( dot(xi-atom_x[a], yi-atom_y[a],
                        zi-atom_z[a]) ) + p_prob;
               const double ratio = (dist==0.0) ? 1.0 : sigma[a]/dist;
               const double ratio6 = ratio*ratio*ratio*ratio*ratio*ratio;
               const double ratio12 = ratio6*ratio6;

               if (p_lj_iwca == 1) {
                  if (ratio*rcfactor > 1) {
                     pr += seta12[a]*ratio12 - seta6[a]*ratio6 + epsilon[a];
                     pa -= epsilon[a];
                  } else {
                     pa = pa - seta6[a]*ratio6 + seta12[a]*ratio12;
                  }
               } else {
                  pr += ratio12*seta12[a];
                  pa -= ratio6*seta6[a];
               }
            }
            potr(x,y,z) = pr;
            pota(x,y,z) = pa;
         }
      }
   }
}

//
//  volumeIntegration
//
double GeometricFlow::volumeIntegration(const Mat<>& f)
{
	double sumf = f.baseInterface().sum();
	return sumf/1000 * p_comdata.deltax() * p_comdata.deltay() * p_comdata.deltaz();
}

//
//  upwinding
//
void GeometricFlow::upwinding(double dt, int nt, 
                              Mat<>& g, Mat<>& su, Mat<>& phitotx)
{
	Mat<> surfnew(su);
	for (int t = 0; t < nt; ++t) {
		for (Stencil<double> phi = su.stencilBegin();
				phi != su.stencilEnd(); ++phi) {
			if (g[phi.i] > 2e-2) {
				surfnew[phi.i] = fmin(1000.0,
						fmax(0.0, *(phi.c) + dt * phi.deriv(phitotx[phi.i])));
			}
		}
		su = surfnew;
	}
}

//
//  initial
//
void GeometricFlow::initial(double xl, double yl, double zl, int n_atom,
		const std::valarray<double>& atom_x, const std::valarray<double>& atom_y,
		const std::valarray<double>& atom_z, const std::valarray<double>& atom_r,
		Mat<>& g, Mat<>& phi)
{
	double dx = p_comdata.deltax(), 
          dy = p_comdata.deltay(), 
          dz = p_comdata.deltaz();
	g = 1.0;
	phi = 0.0;

	double alpha = 1e3;

	for(int a = 0; a < n_atom; ++a) {
		double r = atom_r[a];
		double r2 = r*r;
		double zmin = ((atom_z[a] - zl - r)/dz + 1.0);
		double zmax = ((atom_z[a] - zl + r)/dz + 1.0);

		for(int z = ceil(zmin); z <= floor(zmax); ++z) {
			double distxy = (zl + (z-1)*dz - atom_z[a]);
			double distxy2 = distxy*distxy;
			double rxy2 = fabs(r2 - distxy2);
			double rxy = sqrt(rxy2);
			double ymin = ((atom_y[a] - yl - rxy)/dy + 1.0);
			double ymax = ((atom_y[a] - yl + rxy)/dy + 1.0);

			for(int y = ceil(ymin); y <= floor(ymax); ++y) {
				double distx = (yl + (y-1)*dy - atom_y[a]);
				double distx2 = distx*distx;
				double rx = sqrt(fabs(rxy2 - distx2));
				double xmin = ((atom_x[a] - xl - rx)/dx + 1.0);
				double xmax = ((atom_x[a] - xl + rx)/dx + 1.0);

				for(int x = ceil(xmin); x <= floor(xmax); ++x) {
					g(x,y,z) = 0;
					phi(x,y,z) = alpha;
				}
			}
		}
	}
}

//
//  normalizeSurfAndEps
//
void GeometricFlow::normalizeSurfuAndEps (Mat<>& surfu, Mat<>& eps) 
{

   for (size_t i = 0; i < surfu.size(); i++) {
      if (surfu[i] > 1000.0) {
         surfu[i] = 1000.0;
      }

      if (surfu[i] < 0.0) {
         surfu[i] = 0.0;
      }

      eps[i] = m_pdie + (m_sdie - m_pdie ) *
         ((1000.0 - surfu[i])/1000.0 );
   }
}

//
//  computeSoleng
//
/*
 * Compute soleng1 and soleng2 (solvation).
 * Parameters:
 * 		soleng: The soleng variable to set (compute).  For soleng1, the phi
 *					array should be phi; for soleng2, the phiarray should be
 *					phivoc.
 * 		phi:	Either phi or phivoc array, depending on which soleng
 * 					variable we are computing
 * 		loc_qt:	The loc_qt array.  This is a [3][8][natm] int array, but
 * 					must be passed as a pointer, since natm is a variable.
 * 		charget:	charget array.  This is an [8][natm] int array.
 */
void GeometricFlow::computeSoleng(double& soleng, 
                   Mat<>& phi, Mat<>& charget, Mat<size_t>& loc_qt)
{
   soleng = 0.0;
   for (size_t iind = 1; iind <= charget.nx(); iind++) {
      for (size_t jind = 1; jind <= charget.ny(); jind++) {
         size_t i = loc_qt(iind,jind,1);
         size_t j = loc_qt(iind,jind,2);
         size_t k = loc_qt(iind,jind,3);

         soleng += 0.5 * charget( iind, jind ) * phi(i,j,k);
      }
   }
}

//
// seteqb - "Set Equation B" - set up for the B matrix (Vector) of the non-regularized
// generalized Poission equation that is solved for computing the
// electrostatic potential.
//
// For boundary conditions, the geometric flow (non-regularized)
// currently uses  \phi \rightarrow \phi_{c} (Coulombic potential) at the
// outer boundary which can be realized by 
//  \phi_{c}\left ( x=x_{g} \right )=
//          \sum_{i=1}^{N}\frac{q_{i}}{\varepsilon_{s}\left | x_{g}-x_{i} \right | }
// (q_{i} is a charge at x_{i}), x_{g} is the position at the outer
// boundary, and eps_{s} is the dielectric constant of solvent). Note that
// x_{i} is the position of atoms which have a net/partial charge.
//
//  Setting the boundary to be the value of the charge of the atom
//  weighted by the distance from all the atoms.
//  (Is this the mdh option in APBS?)
//
void GeometricFlow::seteqb(Mat<>& bg, const AtomList& AL, 
      const Mat<>& charget, const Mat<>& corlocqt)
{
   double sum = 0.0;
   for (size_t i = 1; i <= p_comdata.nx(); ++i) 
   {
      for (size_t j = 1; j <= p_comdata.ny(); ++j)
      {
         for (size_t k = 1; k <= p_comdata.nz(); ++k)
         {
            double fp = qb( i, j, k, AL, charget, corlocqt );
            //std::cout << "fp: " << fp << std::endl ;
            int ijk = (i-1) * p_comdata.ny() * 
               p_comdata.nz() + (j-1) * p_comdata.nz() + k - 1;
            bg[ijk] = fp;
            sum += fp;
         }
      }
   }

   std::cout << "sum bg = " << sum << std::endl;
}

//
//  qb
//
double GeometricFlow::qb( size_t i,size_t j,size_t k, const AtomList& AL,
      const Mat<>& charget, const Mat<>& corlocqt )
{
   double x = p_comdata.xvalue(i);
   double y = p_comdata.yvalue(j);
   double z = p_comdata.zvalue(k);
   //std::cout << "x,y,z: " << x << ", " << y << ", " << z << std::endl;
   if(i < 2 || i > p_comdata.nx() - 1 ||
         j < 2 || j > p_comdata.ny() - 1 ||
         k < 2 || k > p_comdata.nz() - 1) 
   {
      double foo = qbboundary( x, y, z, AL );
      //std::cout << "foo: " << foo << std::endl;
      return foo; //qbboundary( x, y, z, AL );
   } else {
      double bar = qbinterior( x, y, z, charget, corlocqt );
      //std::cout << "bar: " << bar << std::endl;
      return bar ; //qbinterior( x, y, z, charget, corlocqt );
   }
}

//
// qbboundary - set the elements on the boundary
//
double GeometricFlow::qbboundary( double x, double y, double z,
      const AtomList& atomList )
{  
   double vbdn = 0;
   for (size_t a = 0; a < atomList.size(); ++a) {
      //
      // vector from the current point (x_{g}) to the atom
      // (x_{i}}
      //
      double x_q = x - atomList.get(a).x(); //xyzr[a][1];
      double y_q = y - atomList.get(a).y(); //xyzr[a][2];
      double z_q = z - atomList.get(a).z(); //xyzr[a][3];
      //std::cout << "atomList: " 
      //   << atomList.get(a).x() << ", " 
      //   << atomList.get(a).y() << ", " 
      //   << atomList.get(a).z() << endl; 
      //std::cout << "x_q,y_q,z_q: " << x_q << ", " 
      //   << y_q << ", " << z_q << std::endl;
      double q_q = atomList.get(a).pqr(); //pqr[a];
      //std::cout << "q_q: " << q_q << std::endl;
      // distance, | x_{g} - x_{i} |
      double rr = sqrt( dot(x_q, y_q, z_q) );  // distance from
      vbdn += q_q/( m_sdie * rr );
      //std::cout << "m_sdie: " << m_sdie << std::endl;
   }
   return vbdn;
}

//
//  qbinterior - laplacian???
//
double GeometricFlow::qbinterior(double x, double y, double z,
      const Mat<>& charget, const Mat<>& corlocqt)
{
   double fp = 0;
   for (size_t a = 1; a <= charget.nx(); ++a) {
      for (size_t ii = 1; ii <= charget.ny(); ++ii) {
         double xc = x - corlocqt(a,ii,1);
         double yc = y - corlocqt(a,ii,2);
         double zc = z - corlocqt(a,ii,3);
         if ( dot(xc,yc,zc) <= 1e-13) {
            fp -= 4.0 * p_comdata.pi() * charget(a,ii)/
                  ( p_comdata.deltax() * p_comdata.deltay() *
                    p_comdata.deltaz() );
         }
      }
   }

   return fp;
}

//
//  pbsolver
//
void GeometricFlow::pbsolver(const Mat<>& eps, Mat<>& phi, const Mat<>& bgf, double tol, int iter)
{
   //cout << "eps: " ; eps.print(); std::cout << std::endl ;
   //cout << "bgf: " ; bgf.print(); std::cout << std::endl ;
	size_t nx = eps.nx(), ny = eps.ny(), nz = eps.nz();
	double dx = p_comdata.deltax(), 
          dy = p_comdata.deltay(), 
          dz = p_comdata.deltaz();

	Mat<> eps1(nx,ny,nz), eps2(nx,ny,nz), eps3(nx,ny,nz);
	for(size_t i = 1; i < nx; ++i) {
		for(size_t j = 1; j < ny; ++j) {
			for(size_t k = 1; k < nz; ++k) {
				eps1(i,j,k) = (eps(i+1,j,k) + eps(i,j,k))/2.0;
				eps2(i,j,k) = (eps(i,j+1,k) + eps(i,j,k))/2.0;
				eps3(i,j,k) = (eps(i,j,k+1) + eps(i,j,k))/2.0;
			}
		}
	}

	std::vector <Eigen::Triplet<double> > tripletList;
	tripletList.reserve(nx*ny*nz);
	Eigen::VectorXd phi_flat(nx*ny*nz);

	size_t n = nx*ny*nz;
	for (size_t i = 1; i <= nx; ++i) {
		for (size_t j = 1; j <= ny; ++j) {
			for(size_t k = 1; k <= nz; ++k) {
				size_t ijk = (i-1)*nz*ny + (j-1)*nz + k-1;
				if (i==1 || i==nx || j==1 || j==ny || k==1 || k==nz) {
					tripletList.push_back(Eigen::Triplet<double>(ijk, ijk, 1.0));
				} else {
					double f = -(  (eps1(i,j,k) + eps1(i-1,j,k))/dx/dx
								 + (eps2(i,j,k) + eps2(i,j-1,k))/dy/dy
								 + (eps3(i,j,k) + eps3(i,j,k-1))/dz/dz );
					tripletList.push_back(Eigen::Triplet<double>(ijk, ijk, f));

					double weit[6];
					weit[0] = eps1(i-1,j,k)/dx/dx;
					weit[1] = eps2(i,j-1,k)/dy/dy;
					weit[2] = eps3(i,j,k-1)/dz/dz;
					weit[3] = eps3(i,j,k)/dz/dz;
					weit[4] = eps2(i,j,k)/dy/dy;
					weit[5] = eps1(i,j,k)/dx/dx;

					assert(ijk > nz*ny);
					size_t jj = ijk - nz*ny;
					tripletList.push_back(Eigen::Triplet<double>(ijk, jj,
							weit[0]));

					assert(ijk > nz);
					jj = ijk - nz;
					tripletList.push_back(Eigen::Triplet<double>(ijk, jj,
							weit[1]));

					assert(ijk > 1);
					jj = ijk - 1;
					tripletList.push_back(Eigen::Triplet<double>(ijk, jj,
							weit[2]));

					assert(ijk + 1 < n);
					jj = ijk + 1;
					tripletList.push_back(Eigen::Triplet<double>(ijk, jj,
							weit[3]));

					assert(ijk + nz < n);
					jj = ijk + nz;
					tripletList.push_back(Eigen::Triplet<double>(ijk, jj,
							weit[4]));

					assert(ijk + nz*ny < n);
					jj = ijk + nz*ny;
					tripletList.push_back(Eigen::Triplet<double>(ijk, jj,
							weit[5]));
				}

				phi_flat(ijk) = phi(i,j,k);
			}
		}
	}

	Eigen::SparseMatrix<double> A(n, n);
	A.setFromTriplets(tripletList.begin(), tripletList.end());
	A.makeCompressed();
   //std::cout << "A: " << A << std::endl;  ??

   //
   //  bi conjugate gradient stabilized solver for sparse square problems.
   //    http://en.wikipedia.org/wiki/Biconjugate_gradient_method
   //
	Eigen::BiCGSTAB<Eigen::SparseMatrix<double>, Eigen::IdentityPreconditioner> solver(A);
	solver.setMaxIterations(iter);
	solver.setTolerance(tol);

	// KTS Note -- I remember being here writing the unit tests, and thinking
	// that this may have had something to do with the difference in the elec
	// energies.  I don't remember the details, but it's something to do with
	// the Eigen solver being different from what is in the Fortran code.
	// phi_flat = solver.solveWithGuess(bgf.baseInterface(), phi_flat);
   // ERJ Note -- Fortran solver:
   // http://sdphca.ucsd.edu/slatec_top/source/dsluom.f (DSLUOM is the
   // Incomplete LU Orthomin Sparse Iterative Ax=b Solver.)
	phi_flat = solver.solve(bgf.baseInterface());
   //std::cout << "phi_flat: " << phi_flat << std::endl;

	for(size_t i = 1; i <= nx; ++i) {
		for(size_t j = 1; j <= ny; ++j) {
			for(size_t k = 1; k <= nz; ++k) {
				size_t ijk = (i-1)*nz*ny + (j-1)*nz + k-1;
				phi(i,j,k) = phi_flat(ijk);
			}
		}
	}
}

void GeometricFlow::write() const
{
}
