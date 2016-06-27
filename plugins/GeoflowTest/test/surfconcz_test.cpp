///  @file    surfconcz_test.cpp
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
/// Copyright (c) 2010-2014 Battelle Memorial Institute. Developed at the
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

#include "modules.h"

/*
 * We test this function against results obtained from the original Fortran
 * code.
 */

class DomainIni : public testing::Test {
protected:
	void SetUp() {
		// These are some lovely globals...  :-/
		comdata.deltax = 2.5;
		comdata.deltay = 2.5;
		comdata.deltaz = 2.5;
		// comdata.dcel = 0.25;
		comdata.pi = acos(-1.0);

		// 1.90 magic?  It's called EXTVALUE.
		domainini(xyzr, natm, 1.90);
	};

	static const size_t natm = 3, foo = 8, bar = 3, baz = 4;

	// These are the first three atoms from the imidazole molecule file.
	double xyzr[natm][baz] = {
		{0.00, 0.00, 0.00, 1.87},
		{1.372, 0.00, 0.00, 1.40},
		{1.764, 1.292, 0.00, 1.87}};
};

TEST_F(DomainIni, TestDimensions) {
	EXPECT_EQ(55, comdata.nx);
	EXPECT_EQ(53, comdata.ny);
	EXPECT_EQ(48, comdata.nz);
}

TEST_F(DomainIni, TestLeftandRight) {
	EXPECT_EQ(-5.9, comdata.xleft);
	EXPECT_EQ(7.6, comdata.xright);

	EXPECT_EQ(-5.9, comdata.yleft);
	EXPECT_EQ(7.1, comdata.yright);

	EXPECT_EQ(-5.9, comdata.zleft);
	EXPECT_EQ(5.85, comdata.zright);
}

TEST_F(DomainIni, TestDcel) {
	EXPECT_EQ(0.25, comdata.dcel);
}
