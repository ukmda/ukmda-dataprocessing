#pragma once
/*
Copyright 2018-2020 Mark McIntyre. 

UKMONLiveCL is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/
#include "..\ukmonlive\UKMonLiveCL.h"
#include "..\shared\tinyxml\tinyxml.h"
#include "..\shared\llsq.h"

int ReadBasicXML(std::string pth, const char* cFileName, long &frcount, long &maxbmax, double &rms)
{
	std::string fname = pth;
	fname += "\\";
	fname += cFileName;

	TiXmlDocument doc(fname.c_str());
	bool loadOkay = doc.LoadFile();

	if (!loadOkay)
	{
		Sleep(500);
		loadOkay = doc.LoadFile();
		if (!loadOkay)
		{
			printf("Could not load %s'. Error='%s'. Exiting.\n", fname.c_str(), doc.ErrorDesc());
			theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 1, L"Unable to open XML file for analysis;", L"");
		}
	}
	else
	{
		TiXmlNode* node = 0;
		TiXmlElement* ufocapture_record = 0;
		TiXmlElement* ufocapture_paths = 0;
		TiXmlElement* uc_path = 0;
		int frames = 0;
		int ret;

		node = doc.FirstChild("ufocapture_record"); // the top level record
		assert(node);
		ufocapture_record = node->ToElement();
		assert(ufocapture_record);
		ret = ufocapture_record->QueryIntAttribute("frames", &frames);
		frcount = frames;

		node = ufocapture_record->FirstChildElement(); // ufocapture_paths 
		assert(node);
		ufocapture_paths = node->ToElement();
		assert(ufocapture_paths);

		int hits;
		ret = ufocapture_paths->QueryIntAttribute("hit", &hits); //get number of hits
		hits = hits > 400 ? 400 : hits; // no need for more than 400 points in a fit

		double x[400], y[400], maxbri = 0;
		double px, py;
		int pb;
		node = ufocapture_paths->FirstChildElement(); // should be the first ua_path line
		assert(node);
		uc_path = node->ToElement();
		assert(uc_path);
		ret = uc_path->QueryDoubleAttribute("x", &px);
		ret = uc_path->QueryDoubleAttribute("y", &py);
		ret = uc_path->QueryIntAttribute("bmax", &pb);
		x[0] = px; y[0] = py;
		maxbri = pb;
		for (int i = 1; i < hits; i++)
		{
			uc_path = uc_path->NextSiblingElement();
			assert(uc_path);
			ret = uc_path->QueryDoubleAttribute("x", &px);
			ret = uc_path->QueryDoubleAttribute("y", &py);
			ret = uc_path->QueryIntAttribute("bmax", &pb);
			x[i] = px; y[i] = py;
			if (pb > maxbri) maxbri = pb;
		}
		maxbmax = (long)maxbri;

		// check for straightness of the fit. Very poor fits are likely to be non-meteoric
		// note that we have to check fit of x to y and y to x because nearly-vertical meteors
		// might have large fit errors in y while still being pretty straight. Fitting in 
		// x instead may produce smaller errors. Ideally we'd fit a line, then calculate the residuals
		// perpendicular to this line. 

		double alpha, beta, l_rms=0, r_rms=0;
		llsq(hits, x, y, alpha, beta, l_rms);
		llsq(hits, y, x, alpha, beta, r_rms);

		// use the smaller of the two values to allow for nearly-vertical events
		rms = (l_rms < r_rms ? l_rms:r_rms);
	}
	return 0;
}

int ReadAnalysisXML(std::string pth, const char* cFileName, double &mag)
{
	int ret;

	std::string fname = pth;
	fname += "\\";
	fname += cFileName;

	TiXmlDocument doc(fname.c_str());
	bool loadOkay = doc.LoadFile();

	if (!loadOkay)
	{
		Sleep(500);
		loadOkay = doc.LoadFile();
		if (!loadOkay)
		{
			printf("Could not load %s'. Error='%s'. Exiting.\n", fname.c_str(), doc.ErrorDesc());
			theEventLog.Fire(EVENTLOG_INFORMATION_TYPE, 1, 1, L"Unable to open XML file for analysis;", L"");
		}
	}
	else
	{
		TiXmlNode* node = 0;
		TiXmlElement* ufoanalyzer_record = 0;
		TiXmlElement* ua2_objects = 0;
		TiXmlElement* ua2_object = 0;

		node = doc.FirstChild("ufoanalyzer_record"); // the top level record
		assert(node);
		ufoanalyzer_record = node->ToElement();
		assert(ufoanalyzer_record);

		node = ufoanalyzer_record->FirstChildElement(); // ufocapture_paths 
		assert(node);
		ua2_objects = node->ToElement();
		assert(ua2_objects);

		node = ua2_objects->FirstChildElement(); // should be the first ua_path line
		assert(node);
		ua2_object = node->ToElement();
		assert(ua2_object);

		double pmg = 99.99;
		ret = ua2_object->QueryDoubleAttribute("mag", &pmg);
		mag = pmg;
	}
	return 0;
}

int ProcessData(std::string pattern, long framelimit, long minbright, char *pth)
{
	std::ofstream csvfile;
	csvfile.open("c:/temp/analysis.csv");
	WIN32_FIND_DATAA data;
	HANDLE hFind = FindFirstFileA(pattern.c_str(), &data);
	if (hFind != INVALID_HANDLE_VALUE) {
		do {
			if (Debug) std::cout << data.cFileName << std::endl;
			long maxbmax=0, frcount=0;
			double mag=99.99;
			double rms = 0;
			ReadBasicXML(pth, data.cFileName, frcount, maxbmax, rms);
			ReadAnalysisXML(pth, data.cFileName, mag);
			csvfile << data.cFileName << "," << maxbmax << "," << frcount << "," << mag << std::endl;
		} while (FindNextFileA(hFind, &data));
		FindClose(hFind);
	}
	csvfile.close();
	return 0;
}