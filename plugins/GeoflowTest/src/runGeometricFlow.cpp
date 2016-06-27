///  @file runGeometricFlow.cpp
///  @author  Elizabeth Jurrus
///  @brief this is a standalone program to run the GeometricFlow Class.
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

#include <iostream>
#include <string>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/ini_parser.hpp>

#include "GeometricFlow.h"
#include "Atom.h"


double getVar( std::string var_name, 
               boost::property_tree::ptree pt, 
               double default_val )
{
   double var_val = default_val;
   try{ 
      var_val = pt.get<double>(var_name); 
      std::cout<< "Variable " << var_name << " set to " << var_val << std::endl ; 
   }
   catch ( std::exception e ) 
   { 
     // std::cout<< "Warning: " << var_name << " not found." << std::endl ; 
   }
   return var_val;
}

int main( int argc, char *argv[] )
{

   GeometricFlow GF;


   if( argc < 2 )
   {
      std::cout << "Usage: " << argv[0]
                << " <atom_name.xyzr> [param_file.param] " << std::endl ;
      exit( 1 );
   }

   //
   //  read in xyzr file name
   //
   std::string xyzr_filename = argv[1];

   //
   //  read in new values for the params
   //
   std::string param_filename;
   if( argc > 2 )
   {
       param_filename = argv[2];
       std::cout << "reading param filename: " << param_filename << std::endl ;

       boost::property_tree::ptree pt;
       boost::property_tree::ini_parser::read_ini(param_filename, pt);

       double expval = getVar( "Geoflow.exper_val", pt, GF.getExperValue() ) ;
       GF.setExperValue( expval );

       double pres_i = getVar( "Geoflow.pres_i", pt, GF.getPressure() ) ;
       GF.setPressure( pres_i );

       double gamma = getVar( "Geoflow.gama_i", pt, GF.getGamma() ) ;
       GF.setGamma( gamma );

       int ffmodel = getVar( "Geoflow.ffmodel", pt, GF.getFFModel() ) ;
       GF.setFFModel( ffmodel );

       double vdwdispersion = getVar( "Geoflow.vdwdispersion", pt, GF.getVDWDispersion() ) ;
       GF.setVDWDispersion( vdwdispersion );

       double extvalue = getVar( "Geoflow.extvalue", pt, GF.getExtValue() ) ;
       GF.setExtValue( extvalue );

       double epsilons = getVar( "Geoflow.sdie", pt, GF.getSDie() ) ;
       GF.setSDie( epsilons );

       double epsilonp = getVar( "Geoflow.pdie", pt, GF.getPDie() ) ;
       GF.setPDie( epsilonp );

   }

   //
   //  Initialize the atom list data structure 
   //
   cout << "reading: " << xyzr_filename << endl ;
   AtomList AL( xyzr_filename, GF.getRadExp(), GF.getFFModel() ); 

   // 
   // Below, are parameters we likely want APBS to access
   //
   //  stub for changing the boundary condition; only one implemented
   //  right now
   //
   //GF.setBoundaryCondition( GeometricFlow::MDH );
   // include the dispersion force between solvent and solute molecules
   // (1/0 = yes/no)
   //GF.setVDWDispersion( vdwdispersion );
   //GF.setGamma( .00001 ); 
   //GF.setGrid( .25 ); // grid size
   //GF.setETolSolvation( .01 ); //error tolerance for solvent
   //GF.setETolSolver( 1e-4 ); //error tolerance for solver
   //GF.setLJWell( 0.1554 ); //Lennard-Jones well depth parameter for water


   //
   //  Setup the geoflow solver
   //
   cout << "seting up..." << endl ;
   struct GeometricFlowOutput geoOut = GF.run( AL );
   
}

