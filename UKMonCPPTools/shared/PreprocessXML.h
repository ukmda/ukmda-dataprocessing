#pragma once
int ReadBasicXML(std::string pth, const char* cFileName, long& frcount, long& maxbmax, double& rms, int& pxls);
int ReadAnalysisXML(std::string pth, const char* cFileName, double& mag);
