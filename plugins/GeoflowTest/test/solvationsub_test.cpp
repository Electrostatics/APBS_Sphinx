///  @file    solvationsub_est.cpp
///  @author  Keith T. Star
///  @brief Unit tests for Geometric Flow
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

#include "gmock/gmock.h"
#include "gtest/gtest.h"

#include "Atom.h"

/*
 * We test this function against results obtained from the original Fortran
 * code.
 */

class ChargeDist : public testing::Test {
protected:
	void SetUp() {
		// These are some lovely globals...  :-/
		//ComData comdata;
		//comdata.init(0.25);

		Atom a(1, 0.0, 0.0, 0.0, 1.87, -0.257);
		Atom b(1, 1.372, 0.0, 0.0, 1.4, -0.317);
		Atom c(1, 1.764, 1.292, 0.0, 1.87, 0.398);
		AtomList AL(

		// 1.90 magic?  It's called EXTVALUE.
		//domainini(xyzr, natm, 1.90);

		// Calculate the charge distribution
//		for (size_t iatm = 1; iatm <= natm; iatm++) {
//			chargedist(xyzr, chratm, charget, corlocqt, loc_qt, iatm);
//		}
	};

	static const size_t natm = 3, foo = 8, bar = 3, baz = 4;

	// These are the first three atoms from the imidazole molecule file.
	double xyzr[natm][baz] = {
		{0.00, 0.00, 0.00, 1.87},
		{1.372, 0.00, 0.00, 1.40},
		{1.764, 1.292, 0.00, 1.87}};
	double chratm[natm] = {-0.257, -0.317, 0.398};
	Mat<> charget {natm, foo};
	Mat<> corlocqt {natm, foo, bar};
	Mat<size_t> loc_qt {natm, foo, bar};
};

TEST_F(ChargeDist, Test_charget_WhateverThatIs) {
	// Test
	double charget_expected[] =  {
		-0.1644800E-01, -0.2467200E-01, -0.2467200E-01, -0.3700800E-01,
		-0.2467200E-01, -0.3700800E-01, -0.3700800E-01, -0.5551200E-01,

		-0.4625664E-01, -0.4463360E-02, -0.6938496E-01, -0.6695040E-02,
		-0.6938496E-01, -0.6695040E-02, -0.104077440,   -0.1004256E-01,

		 0.1270543E-01,  0.2422897E-01,  0.4205937E-01,  0.8020623E-01,
		 0.1905815E-01,  0.3634345E-01,  0.6308905E-01,  0.120309350};

	EXPECT_EQ(natm*foo, charget.baseInterface().size());

	// FLoating point magic refuses to work with EXPECT_DOUBLE_EQ, for some
	// reason that's beyond my ken.
	for (size_t i = 1; i <= natm; i++) {
		for (size_t j = 1; j <= foo; j++) {
			EXPECT_NEAR(charget_expected[(i - 1)*foo + j - 1],
				charget(i, j), .00000001);
		}
	}
}

TEST_F(ChargeDist, Test_corlocqt_WhateverThatIs) {
	// Test
	double corlocqt_expected[] = {
		-0.150, -0.150, -0.150,
		 0.100, -0.150, -0.150,
		-0.150,  0.100, -0.150,
		 0.100,  0.100, -0.150,
		-0.150, -0.150,  0.100,
		 0.100, -0.150,  0.100,
		-0.150,  0.100,  0.100,
		 0.100,  0.100,  0.100,

		1.35, -0.150, -0.150,
		1.60, -0.150, -0.150,
		1.35,  0.100, -0.150,
		1.60,  0.100, -0.150,
		1.35, -0.150,  0.100,
		1.60, -0.150,  0.100,
		1.35,  0.100,  0.100,
		1.60,  0.100,  0.100,

		1.60, 1.10, -0.150,
		1.85, 1.10, -0.150,
		1.60, 1.35, -0.150,
		1.85, 1.35, -0.150,
		1.60, 1.10,  0.100,
		1.85, 1.10,  0.100,
		1.60, 1.35,  0.100,
		1.85, 1.35,  0.100};

	EXPECT_EQ(natm*foo*bar, corlocqt.baseInterface().size());

	// We do it like this becasue EXPECT_FLOAT_EQ wants floats
	// FLoating point magic refuses to work with EXPECT_DOUBLE_EQ, for some
	// reason that's beyond my ken.
	for (size_t i = 1; i <= natm; i++) {
		for (size_t j = 1; j <= foo; j++) {
			for (size_t k = 1; k <= bar; k++) {
				EXPECT_FLOAT_EQ(corlocqt_expected[(i - 1)*foo*bar + (j - 1)*bar + k - 1],
					corlocqt(i, j, k));
			}
		}
	}

	// std::cout << std::endl << "corlocqt";
	// for (size_t i = 1; i <= natm; i++) {
	// 	std::cout << std::endl;
	// 	for (size_t j = 1; j <= foo; j++) {
	// 		std::cout << std::endl;
	// 		for (size_t k = 1; k <= bar; k++) {
	// 			std::cout << corlocqt(i, j, k) << "\t";
	// 		}
	// 	}
	// }
}

TEST_F(ChargeDist, Test_loc_qt_WhateverThatIs) {
	size_t loc_qt_expected[] = {
	24, 24, 24,
	25, 24, 24,
	24, 25, 24,
	25, 25, 24,
	24, 24, 25,
	25, 24, 25,
	24, 25, 25,
	25, 25, 25,

	30, 24, 24,
	31, 24, 24,
	30, 25, 24,
	31, 25, 24,
	30, 24, 25,
	31, 24, 25,
	30, 25, 25,
	31, 25, 25,

	31, 29, 24,
	32, 29, 24,
	31, 30, 24,
	32, 30, 24,
	31, 29, 25,
	32, 29, 25,
	31, 30, 25,
	32, 30, 25};

	EXPECT_EQ(natm*foo*bar, loc_qt.baseInterface().size());

	for (size_t i = 1; i <= natm; i++) {
		for (size_t j = 1; j <= foo; j++) {
			for (size_t k = 1; k <= bar; k++) {
				EXPECT_EQ(loc_qt_expected[(i - 1)*foo*bar + (j - 1)*bar + k - 1],
					loc_qt(i, j, k));
			}
		}
	}
}
