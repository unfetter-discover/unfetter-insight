###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists as a repository of ENGLISH time resolution functions
# These are used to detect the main proper nouns over the course of a document

# Author: William Kinsman
# Date: 2017_04_06

import datefinder
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from scipy.stats import gaussian_kde,mode

def temporal_resolution(text,target='peakclust',strict=True,plot=False):
    """
    given: a text
    @param target = options 'peakclust','lower','upper','mean','all','mode'
    return: target date.
    """
    # find the dates
    dates = [i for i in datefinder.find_dates(text,strict=strict)]
    if len(dates)==0:
        print('No dates found. Switching to non-strict date searching')
        strict = False
        dates = [i for i in datefinder.find_dates(text,strict=False)]
    dates.sort()
    dates_ordinal = [i.toordinal() for i in dates]
        
    # IF soft detection, loop eliminating rediculous outliers until unchanged
    if strict==False and len(dates)>2:
        while True:
            count = len(dates)
            mask          = mad_remove_outliers(dates_ordinal,3.5)
            dates         = [dates[i] for i in xrange(len(dates)) if mask[i]==False]
            dates_ordinal = [dates_ordinal[i] for i in xrange(len(dates_ordinal)) if mask[i]==False]
            if count==len(dates): break
    
    # IF 2 or less dates define data now
    if len(set(dates_ordinal))==2: 
        date_lowerbound = min(dates)
        date_mean       = datetime.fromordinal(int(round(np.mean(dates_ordinal))))
        date_peakclust  = date_mean
        if mode(dates_ordinal).count[0]>1:
            date_mode   = datetime.fromordinal(mode(dates_ordinal).mode[0])
        else:
            date_mode   = None
        date_upperbound = max(dates)
    if len(set(dates_ordinal))==1: 
        print('Returning only date found.')
        return dates[0]
    if len(dates_ordinal)==0: 
        print('No dates found.')
        return None
    
    # IF 2 or more dates perform kernel selection
    if len(set(dates_ordinal))>2:
        # build kernel
        date_range = max(dates_ordinal)-min(dates_ordinal)                 
        density = gaussian_kde(dates_ordinal)
        density.covariance_factor = lambda : .25
        density._compute_covariance()
        x = np.linspace(min(dates_ordinal)-date_range*(.05),max(dates_ordinal)+date_range*(.05),max(date_range*(1.1),200))
        y = density(x)
        
        # output important data
        date_lowerbound = min(dates)
        date_peakclust  = datetime.fromordinal(int(round(x[int(round(np.argmax(y)))])))
        date_mean       = datetime.fromordinal(int(round(np.mean(dates_ordinal))))
        if mode(dates_ordinal).count[0]>1:
            date_mode   = datetime.fromordinal(mode(dates_ordinal).mode[0])
        else:
            date_mode   = None
        date_upperbound = max(dates)
    
    # plot kernel
    if plot==True:
        if len(dates)>2:
            x_scat = dates
            y_scat = -max(y)/3 * np.random.random(len(x_scat))
            
            fig, ax = plt.subplots()
            ax.plot(x,y,color='b')
            fig.autofmt_xdate()
            ax.scatter(x_scat,y_scat,marker='o',c='k',s=20)
            ax.set_xlim(min(x),max(x))
            ax.set_ylim(-max(y)/3,max(y)*1.25)
            ax.set_title('Distribution of Dates  StrictSearch: ' + str(strict))
            ax.set_ylabel('Probability')
            plt.show()
        
        print "Lower bound: {:%b %d, %Y}".format(date_lowerbound)
        print "Peak clust : {:%b %d, %Y}".format(date_peakclust)
        print "Mean       : {:%b %d, %Y}".format(date_mean)
        if date_mode:
            print "Mode       : {:%b %d, %Y}".format(date_mode)
        else:
            print "Mode       : None"
        print "Upper bound: {:%b %d, %Y}".format(date_upperbound)
    
    # return the target date
    return {
        'lower':     date_lowerbound,
        'peakclust': date_peakclust, #default
        'mean':      date_mean,
        'mode':      date_mean,
        'upper':     date_upperbound,
        'all':       dates,
    }[target]

def mad_remove_outliers(vector, thresh=3.5):
    """
    given: points
    return: without outliers
    
    Reference:
    Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
    Handle Outliers", The ASQC Basic References in Quality Control:
    Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
    """
    if isinstance(vector,list):
        points = np.asarray(vector)
    else:
        points = vector
    if len(points.shape) == 1:
        points = points[:,None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)
    
    modified_z_score = 0.6745 * diff / med_abs_deviation
    return modified_z_score > thresh