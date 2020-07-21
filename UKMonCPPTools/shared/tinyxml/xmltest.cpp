/*
   Test program for TinyXML.
*/


#ifdef TIXML_USE_STL
	#include <iostream>
	#include <sstream>
	using namespace std;
#else
	#include <stdio.h>
#endif

#if defined( WIN32 ) && defined( TUNE )
	#include <crtdbg.h>
	_CrtMemState startMemState;
	_CrtMemState endMemState;
#endif

#include "tinyxml.h"

bool XmlTest (const char* testString, const char* expected, const char* found, bool noEcho = false);
bool XmlTest( const char* testString, int expected, int found, bool noEcho = false );

static int gPass = 0;
static int gFail = 0;



bool XmlTest (const char* testString, const char* expected, const char* found, bool noEcho )
{
	bool pass = !strcmp( expected, found );
	if ( pass )
		printf ("[pass]");
	else
		printf ("[fail]");

	if ( noEcho )
		printf (" %s\n", testString);
	else
		printf (" %s [%s][%s]\n", testString, expected, found);

	if ( pass )
		++gPass;
	else
		++gFail;
	return pass;
}


bool XmlTest( const char* testString, int expected, int found, bool noEcho )
{
	bool pass = ( expected == found );
	if ( pass )
		printf ("[pass]");
	else
		printf ("[fail]");

	if ( noEcho )
		printf (" %s\n", testString);
	else
		printf (" %s [%d][%d]\n", testString, expected, found);

	if ( pass )
		++gPass;
	else
		++gFail;
	return pass;
}


void NullLineEndings( char* p )
{
	while( p && *p ) {
		if ( *p == '\n' || *p == '\r' ) {
			*p = 0;
			return;
		}
		++p;
	}
}

//
// This file demonstrates some basic functionality of TinyXml.
// Note that the example is very contrived. It presumes you know
// what is in the XML file. But it does test the basic operations,
// and show how to add and remove nodes.
//

int main()
{
	TiXmlDocument doc("M20200621_230856_TACKLEY_NE.xml");
	bool loadOkay = doc.LoadFile();

	if (!loadOkay)
	{
		printf("Could not load test file 'demotest.xml'. Error='%s'. Exiting.\n", doc.ErrorDesc());
		exit(1);
	}
	doc.Print(stdout);

	TiXmlNode* node = 0;
	TiXmlElement* ufocapture_record = 0;
	TiXmlElement* ufocapture_paths = 0;
	TiXmlElement* uc_path = 0;


	// --------------------------------------------------------
	// An example of changing existing attributes, and removing
	// an element from the document.
	// --------------------------------------------------------

	// Get the "ToDo" element.
	// It is a child of the document, and can be selected by name.
	node = doc.FirstChild("ufocapture_record");
	assert(node);
	ufocapture_record = node->ToElement();
	assert(ufocapture_record);

	node = ufocapture_record->FirstChildElement();
	assert(node);
	ufocapture_paths = node->ToElement(); 
	assert(ufocapture_paths);

	int hits;
	int ret;
	double px, py;

	ret=ufocapture_paths->QueryIntAttribute("hit", &hits);
	hits = hits > 200 ? 200 : hits; // don't need more than 200 points to do RMS
	double x[200], y[200];
	node = ufocapture_paths->FirstChildElement(); // should be the first ua_path line
	uc_path = node->ToElement(); 
	ret=uc_path->QueryDoubleAttribute("x", &px);
	ret = uc_path->QueryDoubleAttribute("y", &py);
	x[0] = px; y[0] = py;
	int i;
	for (i = 1; i < hits; i++)
	{
		uc_path= uc_path->NextSiblingElement();
		assert(uc_path);
		ret=uc_path->QueryDoubleAttribute("x", &px);
		ret = uc_path->QueryDoubleAttribute("y", &py);
		x[i] = px; y[i] = py;
	}
	for (i = 0; i < hits; i++)
		printf("%d %f %f\n", i, x[i], y[i]);
}
