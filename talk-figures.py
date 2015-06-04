import os
import numpy as np
import pylab as plt

from astrometry.util.plotutils import *

from utils import *

# Github's PDF renderer doesn't seem to like PDF figures!
plotformat = 'png'
        
def example1d():
    means = [ 4  , 8   ]
    stds  = [ 1.5, 1   ]
    amps  = [ 0.7, 0.3 ]

    K = len(means)
    N = 300
    amps = np.array(amps)
    amps /= np.sum(amps)
    nk = np.random.multinomial(N, amps)
    print 'nk', nk
    x = []
    for n,mean,std in zip(nk, means, stds):
        x.extend(np.random.normal(loc=mean, scale=std, size=n))

    plt.clf()
    plt.hist(x, histtype='step', range=(0,12), bins=25)
    plt.savefig('ex1.png')    


def example2d():
    means = [ (4,3.5)  , (8,4.5) ]
    stds  = [ 1.5, 1   ]
    amps  = [ 0.7, 0.3 ]

    K = len(means)
    D = 2
    N = 300
    amps = np.array(amps)
    amps /= np.sum(amps)
    nk = np.random.multinomial(N, amps)
    print 'nk', nk
    x = []
    for n,mean,std in zip(nk, means, stds):
        x.append(np.random.normal(loc=mean, scale=std, size=(n,D)))

    print [xi.shape for xi in x]

    ax = [-1, 11, -1, 9]
    for colors,plotname in [('bb','a'), ('br','b')]:
        plt.clf()
        for xi,cc in zip(x, colors):
            plt.plot(xi[:,0], xi[:,1], 'o', color=cc, mec='none', alpha=0.8)
            plt.plot(xi[:,0], xi[:,1], 'o', color='k', mfc='none', alpha=0.5)
        plt.axis(ax)
        plt.xticks([]); plt.yticks([])
        plt.savefig('ex2%s.pdf' % plotname)


def example3():
    C,ax = get_clusters_A()
    x = sample_clusters(*C, N=200)
    
    for colors,plotname in [('kkk','a'), ('brg','b')]:
        plt.clf()
        for xi,cc in zip(x, colors):
            plt.plot(xi[:,0], xi[:,1], 'o', color=cc, mec='none', alpha=0.8)
            #plt.plot(xi[:,0], xi[:,1], 'o', color=cc, mec='none')
            plt.plot(xi[:,0], xi[:,1], 'o', mec='k', mfc='none', alpha=0.1)

        # import matplotlib as mpl
        # for m,s,c in zip(means, stds, colors):
        #     plt.gca().add_patch(mpl.patches.Circle(
        #         m, radius=s, ec=c, fc='none', zorder=20, lw=3))
        plt.axis(ax)
        plt.xticks([]); plt.yticks([])
        plt.xlabel('Measurement A')
        plt.ylabel('Measurement B')
        #plt.axis('equal')
        plt.savefig('ex3%s.%s' % (plotname, plotformat))



def kmeans(ps, seed=None, getcluster=get_clusters_A, K=3, N=200,
           plotTruth=False, truthOrder=None, plotsymbol='.'):
    C,ax = getcluster()
    X = sample_clusters(*C, N=N, bounds=np.array(ax).reshape(2,2))
    xi = X
    X = np.vstack(X)
    print X.shape

    if seed is not None:
        np.random.seed(seed)
    centroids = X[np.random.permutation(N)[:K],:]
    print 'centroids', centroids

    while True:
        # compute nearest centroid for data points
        dists = distance_matrix(centroids, X)
        print 'dists', dists.shape
        #print 'dists', dists
        nearest = np.argmin(dists, axis=0)
        print 'nearest', nearest.shape, np.unique(nearest)
        #print nearest
        
        plt.clf()
        for i,c in enumerate(centroids):
            plt.plot(c[0], c[1], 'x', mew=2, ms=15, color=colors[i])
        for i,c in enumerate(centroids):
            I = np.flatnonzero(nearest == i)
            plt.plot(X[I,0], X[I,1], plotsymbol, mfc=colors[i], mec='k')


        vor = None
        if K > 2:
            from scipy.spatial import Voronoi #, voronoi_plot_2d
            vor = Voronoi(centroids)
            voronoi_plot_2d(vor, plt.gca())
        else:
            mid = np.mean(centroids, axis=0)
            x0,y0 = centroids[0]
            x1,y1 = centroids[1]
            slope = (y1-y0)/(x1-x0)
            slope = -1./slope
            run = 1000.
            plt.plot([mid[0] - run, mid[0] + run],
                     [mid[1] - run*slope, mid[1] + run*slope], 'k--')
                     

        plt.axis(ax)
        plt.xticks([]); plt.yticks([])
        ps.savefig()

        newcentroids = []
        for i,c in enumerate(centroids):
            I = np.flatnonzero(nearest == i)
            newcentroids.append((np.mean(X[I,:], axis=0)))

        plt.clf()
        for i,(oc,nc) in enumerate(zip(centroids, newcentroids)):
            plt.plot(oc[0], oc[1], 'kx', mew=2, ms=10)
            plt.arrow(oc[0], oc[1],nc[0]-oc[0], nc[1]-oc[1], color=colors[i])
            plt.plot(nc[0], nc[1], 'x', mew=2, ms=15, color=colors[i])
        for i,c in enumerate(centroids):
            I = np.flatnonzero(nearest == i)
            plt.plot(X[I,0], X[I,1], plotsymbol, mfc=colors[i], mec='k')

        if vor is not None:
            voronoi_plot_2d(vor, plt.gca())
        else:
            plt.plot([mid[0] - run, mid[0] + run],
                     [mid[1] - run*slope, mid[1] + run*slope], 'k--')
        plt.axis(ax)
        plt.xticks([]); plt.yticks([])
        ps.savefig()

        newcentroids = np.array(newcentroids)

        print 'Centroid difference:', newcentroids - centroids
        
        if np.max(np.abs(centroids - newcentroids)) < 1e-8:
            break
        
        centroids = newcentroids

    if plotTruth:
        plt.clf()
        for i,x in enumerate(xi):
            ii = i
            if truthOrder is not None:
                ii = truthOrder[i]
            plt.plot(x[:,0], x[:,1], plotsymbol, mfc=colors[ii], mec='k')
        for i,(a,mu,s) in enumerate(zip(*C)):
            ii = i
            if truthOrder is not None:
                ii = truthOrder[i]
            plt.plot(mu[0], mu[1], 'x', mew=2, ms=15, color=colors[ii])
        plt.axis(ax)
        plt.xticks([]); plt.yticks([])
        ps.savefig()
        

def get_clusters_B():
    means = [ (5., 4.), (5., 4.) ]
    stds  = [ 4., 0.2  ]
    amps  = [ 0.8, 0.2 ]
    ax = [0, 10, 0, 8]
    return (amps, means, stds), ax

        
def kmeans_break1():
    seed = 42
    ps = PlotSequence('break1', suffix=plotformat)

    np.random.seed(seed)
    kmeans(ps, seed=None, getcluster=get_clusters_B, K=2, plotTruth=True,
           plotsymbol='o')

    # C,ax = get_clusterB()
    # np.random.seed(seed)
    # N = 200
    # X = sample_clusters(*C, N=N, bounds=np.array(ax).reshape(2,2))
    # 
    # plt.clf()
    # for i,xi in enumerate(X):
    #     plt.plot(xi[:,0], xi[:,1], '.', 

def kmeans_break2():
    ps = PlotSequence('break2', suffix='png')

    np.random.seed(42)    
    kmeans(ps, seed=None, getcluster=get_clusters_C, K=2, plotTruth=True,
           plotsymbol='o', truthOrder=[1,0], N=500)

def sample_gmm(amps, means, covs, N=100, D=2, bounds=None):
    K = len(amps)
    amps = np.array(amps)
    amps /= np.sum(amps)
    nk = np.random.multinomial(N, amps)
    x = []
    trueclass = []
    for n,mean,cov in zip(nk, means, covs):
        u,s,v = np.linalg.svd(cov)
        # angle = np.linspace(0., 2.*np.pi, 200)
        # u1 = u[0,:]
        # u2 = u[1,:]
        # s1,s2 = np.sqrt(s)
        # xy = (u1[np.newaxis,:] * s1 * np.cos(angle)[:,np.newaxis] +
        #       u2[np.newaxis,:] * s2 * np.sin(angle)[:,np.newaxis])

        xi = np.random.normal(size=(n,D))
        print 'xi', xi.shape
        xi = mean + np.dot(u, (xi * s).T).T
        
        if bounds is not None:
            outofbounds = np.empty(len(xi), bool)
            while True:
                outofbounds[:] = False
                for d,(lo,hi) in enumerate(bounds):
                    outofbounds |= np.logical_or(xi[:,d] < lo, xi[:,d] > hi)
                if not np.any(outofbounds):
                    break
                I = np.flatnonzero(outofbounds)
                newxi = np.random.normal(size=(len(I),D))
                xi[I,:] = mean + np.dot(u, (newxi * s).T).T
            
        x.append(xi)
    print [xi.shape for xi in x]
    return x

def gmm1():
    amps = [0.8, 0.2]
    means = [ (3., 4.), (6.5, 4.) ]
    covs = [ np.array([[1.,-0.5],[-0.5,1.]]),
             np.array([[1.,0.5],[0.5,1.]]),
             ]
    N = 1000
    X = sample_gmm(amps, means, covs, N=N)

    ps = PlotSequence('gmm', suffix=plotformat)

    order = [1,0]
    
    plt.clf()
    for i,xi in enumerate(X):
        plt.plot(xi[:,0], xi[:,1], '.', color=colors[order[i]])
    # plt.axis('scaled')
    plt.axis('equal')
    ps.savefig()
    ax = plt.axis()

    #ax = [0, 10, 0, 8]
    
    K = 2

    amps = np.ones(K) / K
    means = np.random.normal(size=(K,2)) * 2
    means[:,0] += (ax[0]+ax[1])/2.
    means[:,1] += (ax[2]+ax[3])/2.
    covs = [np.eye(2) for i in range(K)]

    Xi = X
    X = np.vstack(X)
    
    for i in range(25):
        z = np.zeros((K,N))
        for k,(amp,mean,cov) in enumerate(zip(amps, means, covs)):

            print 'Component K: amp', amp, 'mean', mean, 'cov', cov

            z[k,:] = amp * gaussian_probability(X, mean, cov)

        # plt.clf()
        # plt.plot(X[:,0], X[:,1], 'k.')
        # for k,(amp,mean,cov) in enumerate(zip(amps, means, covs)):
        #     u,s,v = np.linalg.svd(cov)
        #     angle = np.linspace(0., 2.*np.pi, 200)
        #     u1 = u[0,:]
        #     u2 = u[1,:]
        #     s1,s2 = np.sqrt(s)
        #     xy = (u1[np.newaxis,:] * s1 * np.cos(angle)[:,np.newaxis] +
        #           u2[np.newaxis,:] * s2 * np.sin(angle)[:,np.newaxis])
        #     plt.plot(mean[0] + xy[:,0], mean[1] + xy[:,1], '-', color=colors[k], lw=2)
        # zmax = np.argmax(z, axis=0)
        # print 'zmax', zmax.shape
        # 
        # for k in range(K):
        #     I = np.flatnonzero(zmax == k)
        #     plt.plot(X[I,0], X[I,1], 'o', mec=colors[k], mfc='none')
        # 
        # ps.savefig()

        plt.clf()
        # snazzy red/blue color coding
        cc = np.zeros((N,3))
        cc[:,2] = z[0,:] / np.sum(z, axis=0)
        cc[:,0] = z[1,:] / np.sum(z, axis=0)
        plt.scatter(X[:,0], X[:,1], color=cc, s=9, alpha=0.5)
        #plt.plot(X[:,0], X[:,1], 'o', mec='k', mfc='none', ms=3, alpha=0.1)

        for k,(amp,mean,cov) in enumerate(zip(amps, means, covs)):
            u,s,v = np.linalg.svd(cov)
            angle = np.linspace(0., 2.*np.pi, 200)
            u1 = u[0,:]
            u2 = u[1,:]
            s1,s2 = np.sqrt(s)
            xy = (u1[np.newaxis,:] * s1 * np.cos(angle)[:,np.newaxis] +
                  u2[np.newaxis,:] * s2 * np.sin(angle)[:,np.newaxis])
            plt.plot(mean[0] + xy[:,0], mean[1] + xy[:,1], 'k-', lw=4)
            plt.plot(mean[0] + xy[:,0], mean[1] + xy[:,1], '-', color=colors[k], lw=2)

        plt.axis(ax)
        ps.savefig()

        z /= np.sum(z, axis=0)

        newamps = np.sum(z, axis=1)
        newamps /= np.sum(newamps)
        print 'new amps', newamps
        newmeans = [np.sum(z[k,:][np.newaxis,:] * X.T, axis=1) / np.sum(z[k,:])
                    for k in range(K)]
        print 'new means', newmeans
        newcovs = [np.dot(z[k,:] * (X - mean).T, X - mean) / np.sum(z[k,:])
                   for k,mean in enumerate(means)]
        print 'new covs', newcovs

        amps = newamps
        means = newmeans
        covs = newcovs
        
def fgbg_example():
    import utils
    # Here's our foreground-background synthetic dataset:
    xlo,xhi = 0,10
    ylo,yhi = 0,8
    # Here are the real objects in our sample:
    amp_true = 3
    offset_true = 4
    Nf = 200
    sf = 0.5
    xf = np.linspace(xlo, xhi, Nf)
    yf = offset_true + amp_true * np.sin(xf) + np.random.normal(scale=sf, size=Nf)
    # And here are the background objects
    Nb = 400
    xb = np.random.uniform(xlo, xhi, size=Nb)
    yb = np.random.uniform(ylo, yhi, size=Nb)
    Xi = [np.vstack((xf,yf)).T, np.vstack((xb,yb)).T]
    X = np.vstack(Xi)
    sigmas = np.zeros(Nf+Nb) + sf
    
    fg_true = Nf / float(Nf + Nb)

    plt.clf()
    utils.plot_sinusoid_samples([X], xf, np.zeros((0,3)))
    plt.title('Foreground-background data');
    plt.axis([xlo,xhi,ylo,yhi])
    # save for talk slides!
    plt.savefig('fgbg-0.pdf');
    
    plt.clf()
    #for i,x in enumerate(Xi):
    #    plt.plot(x[:,0], x[:,1], 'o', color=utils.colors[i], ms=3)
    utils.plot_sinusoid_samples(Xi, xf, np.zeros((0,3)))
    plt.title('Foreground-background data');
    plt.axis([xlo,xhi,ylo,yhi])
    # save for talk slides!
    plt.savefig('fgbg-1.pdf');

    # Log posterior probability for our sinusoidal foreground-background model.
    def sinusoid_logprob(params, X, sigmas, ylo, yhi):
        # Unpack the parameter vector
        fg, offset, amp = params
        # If the foreground amplitude is outside the range [0,1], return
        if not 0 <= fg <= 1:
            return -np.inf
        # Pull out the 'x' and 'y' coordinates of the data
        x = X[:,0]
        y = X[:,1]
        # The foreground likelihood is a Gaussian around the predicted y.
        ypred = offset + amp * np.sin(x)
        likelihood = fg * utils.gaussian_probability_1d(y, ypred, sigmas**2)
        # The background likelihood is just a uniform value.
        # In order to be normalized, we need the constant value to 
        # integrate to 1 over the range (yhi-ylo)
        likelihood += (1 - fg) * 1/(yhi - ylo)
        # Bad Bayesian!  No cookie!
        logposterior = np.sum(np.log(likelihood)) + 0.
        return logposterior

    # If we haven't already...
    import emcee
    
    # Initialization...
    nwalkers = 50
    
    # Foreground weight
    fg = 0.5
    # Sinusoidal offset
    offset = (yhi + ylo) / 2.
    # Sinusoidal amplitude
    amp = (yhi - ylo)/4.
    
    # Parameter vector
    p0 = np.array([fg, offset, amp])
    
    # Scatter initial walker positions around p0.
    pp = np.vstack([p0 + np.random.normal(scale=0.1, size=len(p0))
                    for i in range(nwalkers)])
    ndim = len(p0)
    print 'Number of dimensions to sample:', ndim
    
    # Now create the emcee Sampler object, giving it our "sinusoid_logprob" function.
    sampler = emcee.EnsembleSampler(nwalkers, ndim, sinusoid_logprob, args=(X, sigmas, ylo, yhi))
    
    # Cavalierly ignore some numerical warnings (overflow/underflow because
    # we're working in probability rather than log-prob space in gmm_logprob)
    np.seterr(all='ignore')
    # During development, you may run this more than once... reset the sampler state.
    sampler.reset()
    # Run the sampler!  This will take a few seconds to run.
    pos,logprob,state = sampler.run_mcmc(pp, 1000)
    
    utils.plot_sinusoid_samples(Xi, xf, pos)
    plt.axis([xlo,xhi,ylo,yhi])
    plt.title('Sinusoid: final samples');
    plt.savefig('fgbg-2.pdf')
    
plt.figure(figsize=(4,3))
plt.subplots_adjust(left=0.1, right=0.98, bottom=0.1, top=0.95)
    
np.random.seed(42)    
#example1d()
#example2d()
#example3()

plt.subplots_adjust(left=0.1, right=0.98, bottom=0.1, top=0.9)
fgbg_example()
sys.exit(0)

ps = PlotSequence('kmeans', suffix=plotformat)
np.random.seed(42)    
kmeans(ps)

sys.exit(0)

# 
# ps = PlotSequence('kmeans2', suffix='png')
# np.random.seed(42)    
# kmeans(ps, seed=9)
# os.system('avconv -r 4 -y -i kmeans2-%02d.png kmeans2.mov')

plt.subplots_adjust(left=0.01, right=0.99, bottom=0.01, top=0.99)
np.random.seed(42)    
kmeans_break1()
#kmeans_break2()

np.random.seed(42)    
gmm1()

