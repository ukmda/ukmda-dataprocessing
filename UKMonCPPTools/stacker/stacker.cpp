// Simple stacking tool using OpenCV
// copied from startrails programme and adapted for Windows
// by Mark McIntyre, 2020
// Copyright 2018 Jarno Paananen <jarno.paananen@gmail.com>
// Based on script by Thomas Jacquin
// SPDX-License-Identifier: MIT

#include <cstdlib>
#ifndef _WIN32
#include <glob.h>
#endif
#include <string>
#include <iostream>
#include <vector>
#include <algorithm>

#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>

#define KNRM "\x1B[0m"
#define KRED "\x1B[31m"
#define KGRN "\x1B[32m"
#define KYEL "\x1B[33m"
#define KBLU "\x1B[34m"
#define KMAG "\x1B[35m"
#define KCYN "\x1B[36m"
#define KWHT "\x1B[37m"

#ifdef _WIN32
typedef struct {size_t gl_pathc; char **gl_pathv;size_t gl_offs;} glob_t;
int  glob(const char *, int, int (*)(const char *, int), glob_t *);
void globfree(glob_t *);
char* basename(char *);
#endif
//-------------------------------------------------------------------------------------------------------
//-------------------------------------------------------------------------------------------------------

int main(int argc, char *argv[])
{
    if (argc != 5)
    {
        std::cout << KRED
                  << "You need to pass 4 arguments: source directory, file extension, brightness treshold, output file"
                  << KNRM << std::endl;
        std::cout << "    ex: startrails ../images/20180208/ jpg 0.07 startrails.jpg" << std::endl;
        std::cout << "    brightness ranges from 0 (black) to 1 (white)" << std::endl;
        std::cout << "    A moonless sky is around 0.05 while full moon can be as high as 0.4" << std::endl;
        return 3;
    }
    std::string directory  = argv[1];
    std::string extension  = argv[2];
    double threshold       = atof(argv[3]);
    std::string outputfile = argv[4];

    // Find files
    glob_t files;
    std::string wildcard = directory + "/*." + extension;
    glob(wildcard.c_str(), 0, NULL, &files);
    if (files.gl_pathc == 0)
    {
        globfree(&files);
        std::cout << "No images found, exiting." << std::endl;
        return 0;
    }
    cv::Mat accumulated;

    // Create space for statistics
    cv::Mat stats;
    stats.create(1, (int)files.gl_pathc, CV_64F);

    for (size_t f = 0; f < files.gl_pathc; f++)
    {
#ifndef _WIN32
		std::string fname = files.gl_pathv[f];
#else
		std::string fname = directory + "/" + files.gl_pathv[f];
#endif
        cv::Mat image = cv::imread(fname, cv::IMREAD_UNCHANGED);
        if (!image.data)
        {
            std::cout << "Error reading file " << basename(files.gl_pathv[f]) << std::endl;
            stats.col((int)f) = 1.0; // mark as invalid
            continue;
        }

        cv::Scalar mean_scalar = cv::mean(image);
        double mean;
        switch (image.channels())
        {
            default: // mono case
                mean = mean_scalar.val[0];
                break;
            case 3: // for color choose maximum channel
            case 4:
                mean = cv::max(mean_scalar[0], cv::max(mean_scalar[1], mean_scalar[2]));
                break;
        }
        // Scale to 0-1 range
        switch (image.depth())
        {
            case CV_8U:
                mean /= 255.0;
                break;
            case CV_16U:
                mean /= 65535.0;
                break;
        }
        std::cout << "[" << f + 1 << "/" << files.gl_pathc << "] " << basename(files.gl_pathv[f]) << " " << mean
                  << std::endl;

        stats.col((int)f) = mean;

        if (mean <= threshold)
        {
            if (accumulated.empty())
            {
                image.copyTo(accumulated);
            }
            else
            {
                accumulated = cv::max(accumulated, image);
            }
        }
    }

    // Calculate some statistics
    double min_mean, max_mean;
    cv::Point min_loc;
    cv::minMaxLoc(stats, &min_mean, &max_mean, &min_loc);
    double mean_mean = cv::mean(stats)[0];

    // For median, do partial sort and take middle value
    std::vector<double> vec;
    stats.copyTo(vec);
    std::nth_element(vec.begin(), vec.begin() + (vec.size() / 2), vec.end());
    double median_mean = vec[vec.size() / 2];

    std::cout << "Minimum: " << min_mean << " maximum: " << max_mean << " mean: " << mean_mean
              << " median: " << median_mean << std::endl;

    // If we still don't have an image (no images below threshold), copy the minimum mean image so we see why
    if (accumulated.empty())
    {
        std::cout << "No images below threshold, writing the minimum image only " << std::endl;
#ifndef _WIN32
		std::string fname = files.gl_pathv[min_loc.x];
#else
		std::string fname = directory + "/" + files.gl_pathv[min_loc.x];
#endif
        accumulated = cv::imread(fname, cv::IMREAD_UNCHANGED);
    }
    globfree(&files);

    std::vector<int> compression_params;
    compression_params.push_back(CV_IMWRITE_PNG_COMPRESSION);
    compression_params.push_back(9);
    compression_params.push_back(CV_IMWRITE_JPEG_QUALITY);
    compression_params.push_back(95);

    cv::imwrite(outputfile, accumulated, compression_params);
    return 0;
}
#ifdef _WIN32
#include <windows.h>
int glob(const char *path, int a, int b(const char *x, int y), glob_t *flist)
{
	HANDLE dir;
	WIN32_FIND_DATA file_data;
	size_t nimgs=0;

	if ((dir = FindFirstFile(path, &file_data)) == INVALID_HANDLE_VALUE)
	{
		flist->gl_pathc=0;
        return 0; /* No files found */
	}
	do {
		nimgs++;
	} while (FindNextFile(dir, &file_data));
	flist->gl_pathv=(char**)calloc(nimgs, sizeof(char*));
	flist->gl_pathc=nimgs;
	//std::cout << nimgs << std::endl;

	dir = FindFirstFile(path, &file_data);
	nimgs=0;
	do {
		size_t s = strlen(file_data.cFileName);
		flist->gl_pathv[nimgs]=(char*)calloc(s+1, sizeof(char));
		strncpy(flist->gl_pathv[nimgs], file_data.cFileName, s);
		//std::cout << flist->gl_pathv[nimgs]<< std::endl;
		nimgs++;
	} while (FindNextFile(dir, &file_data));

	return 0;
}
void globfree(glob_t *flist)
{
	for(int i=0;i<flist->gl_pathc;i++)
		free(flist->gl_pathv[i]);
	free(flist->gl_pathv);
}

// just return the filename, no need to get clever here
char* basename(char *path)
{
	return path;
}
#endif