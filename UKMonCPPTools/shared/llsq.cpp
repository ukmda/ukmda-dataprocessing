# include <math.h>
# include <stdio.h>
# include <stdlib.h>
# include <time.h>

# include "llsq.h"
static double getrms(double x[], double y[], double a, double b, int n);

/******************************************************************************/

void llsq0 ( int n, double x[], double y[], double &a, double &rms )

/******************************************************************************/
/*
  Purpose:

    LLSQ0 solves a linear least squares problem matching y=a*x to data.

  Discussion:

    A formula for a line of the form Y = A * X is sought, which
    will minimize the root-mean-square error to N data points ( X[I], Y[I] );

  Licensing:

    This code is distributed under the GNU LGPL license. 

  Modified:

    15 January 2019

  Author:

    John Burkardt

  Parameters:

    Input, int N, the number of data values.

    Input, double X[N], Y[N], the coordinates of the data points.

    Output, double *A, the slope of the least-squares approximant to the data.
*/
{
  double bot;
  int i;
  double top;
/*
  Special case.
*/
  if ( n == 1 )
  {
    if ( x[0] == 0.0 )
    {
      a = 1.0;
    }
    else
    {
      a = y[0] / x[0];
    }
    rms = 0;
    return;
  }
/*
  Compute (x'y)/(x'x).
*/
  top = 0.0;
  bot = 0.0;
  for ( i = 0; i < n; i++ )
  {
    top = top + x[i] * y[i];
    bot = bot + x[i] * x[i];
  }
  a = top / bot;

  // calc residuals and RMS
  rms = getrms(x, y, a, 0, n);

  return;
}
/******************************************************************************/

void llsq ( int n, double x[], double y[], double &a, double &b, double& rms )

/******************************************************************************/
/*
  Purpose:

    LLSQ solves a linear least squares problem matching y=a*x+b  to data.

  Discussion:

    A formula for a line of the form Y = A * X + B is sought, which
    will minimize the root-mean-square error to N data points ( X[I], Y[I] );

  Licensing:

    This code is distributed under the GNU LGPL license. 

  Modified:

    07 March 2012

  Author:

    John Burkardt

  Parameters:

    Input, int N, the number of data values.

    Input, double X[N], Y[N], the coordinates of the data points.

    Output, double *A, *B, the slope and Y-intercept of the least-squares
    approximant to the data.
*/
{
  double bot;
  int i;
  double top;
  double xbar;
  double ybar;
/*
  Special case.
*/
  if ( n == 1 )
  {
    a = 0.0;
    b = y[0];
    rms = 0;
    return;
  }
/*
  Average X and Y.
*/
  xbar = 0.0;
  ybar = 0.0;
  for ( i = 0; i < n; i++ )
  {
    xbar = xbar + x[i];
    ybar = ybar + y[i];
  }
  xbar = xbar / ( double ) n;
  ybar = ybar / ( double ) n;
/*
  Compute Beta.
*/
  top = 0.0;
  bot = 0.0;
  for ( i = 0; i < n; i++ )
  {
    top = top + ( x[i] - xbar ) * ( y[i] - ybar );
    bot = bot + ( x[i] - xbar ) * ( x[i] - xbar );
  }
  a = top / bot;

  b = ybar - a * xbar;

  // calc residuals and RMS
  rms = getrms(x, y, a, b, n);

  return;
}

static double getrms(double x[], double y[], double a, double b, int n)
{
    double yn=0, rms=0;
    double resids = 0;
    for (int i = 0; i < n; i++)
    {
        yn = a * x[i] + b;
        resids += pow(yn - y[i], 2);
    }
    rms = sqrt(resids / n);
    return rms;
}