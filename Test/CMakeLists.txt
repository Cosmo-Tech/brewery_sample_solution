# Confidential - All rights reserved - Cosmo Tech - 2018
# This document and all information contained herein is the exclusive property
# - including all intellectual property rights pertaining thereto - of The
# CoSMo Company. Any use, reproduction, translation, broadcasting,
# transmission, distribution, etc., to any person is prohibited unless it
# has been previously and specifically authorized by written means by The
# CoSMo Company. The CoSMo Company will use any legal mean at its disposal
# to put an end to any illicit or prohibited act and obtain full
# compensation.
set(EXE_NAME main -P ${CMAKE_CURRENT_SOURCE_DIR} -f)

csmAddTest(BreweryTutorialSimulation ${EXE_NAME} -i BreweryTutorialSimulation)

csmAddTest(Deutero ${EXE_NAME} -i BreweryTutorialSimulation)

csmAddTest(Trito ${EXE_NAME} -i BreweryTutorialSimulation)

if(EXAMPLES_MATHGL_DISPLAY)
  csmAddTest(Simulation_1 ${EXE_NAME} -i Simulation_1 -E ${CEX_PLUGINS_DIR} INSTALL)
  csmSetTestsProperties(Simulation_1 PROPERTIES FAIL_REGULAR_EXPRESSION "Cannot connect to probe")
endif()
