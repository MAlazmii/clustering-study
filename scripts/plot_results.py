#!/usr/bin/env python3
"""Generate two scientific figures from verified local evidence; outputs must be new."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from clustering_study.experiment import verify_run

BG, INK, MUTED = '#111c26', '#f2f3eb', '#aebcca'
COLORS = {'random':'#ffcc80', 'plus':'#57d9c2', 'bisect':'#b6a4ff'}
NAMES = {'random':'Random start', 'plus':'k-means++', 'bisect':'Bisecting'}
TITLES = {'separated':'Separated', 'overlap':'Overlapping', 'anisotropic':'Stretched'}


def decorate(ax):
    ax.set_facecolor(BG)
    ax.tick_params(colors=MUTED,labelsize=10)
    for spine in ax.spines.values():spine.set_color('#394752')
    ax.grid(axis='y',color='#394752',alpha=.5)


def save(fig, output, name):
    fig.savefig(output/f'{name}.png',dpi=180,facecolor=BG)
    fig.savefig(output/f'{name}.svg',facecolor=BG,metadata={'Date':None})
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    record=verify_run(args.run)
    config=record['config']
    if config['cases']!=['separated','overlap','anisotropic'] or config['methods']!=['random','plus','bisect']:
        raise ValueError('Figure layout requires the three documented cases and methods')
    args.output.mkdir(parents=True,exist_ok=False)
    plt.rcParams.update({'font.family':'DejaVu Sans','svg.hashsalt':'clustering-study-v1'})
    fig,axes=plt.subplots(2,3,figsize=(14,9),facecolor=BG)
    fig.subplots_adjust(left=.075,right=.975,top=.77,bottom=.20,hspace=.36,wspace=.23)
    fig.text(.065,.92,'CLUSTERING / UNDER THE SURFACE',color=INK,fontsize=25,weight='bold')
    fig.text(.065,.867,'The geometry matters. A good-looking partition can still miss the generating groups.',color=MUTED,fontsize=13)
    ari_lower = min(-.08, min(r['ari'] for r in record['runs'])-.05)
    for col,case in enumerate(config['cases']):
        for row,metric in enumerate(['ari','silhouette']):
            ax=axes[row,col];decorate(ax)
            for j,method in enumerate(config['methods']):
                runs=sorted((r for r in record['runs'] if r['case']==case and r['method']==method),key=lambda r:(r['dataset_seed'],r['init_seed']))
                values=np.array([r[metric] for r in runs],dtype=float)
                if not np.isfinite(values).all():raise ValueError('Undefined metric cannot be plotted as a number')
                xs=j+np.linspace(-.14,.14,len(values))
                color=COLORS[method]
                ax.scatter(xs,values,s=17,color=color,alpha=.4,zorder=2)
                q1,med,q3=np.quantile(values,[.25,.5,.75])
                ax.vlines(j,values.min(),values.max(),color=color,alpha=.45,lw=1,zorder=3)
                ax.vlines(j,q1,q3,color=color,lw=6,zorder=4)
                ax.scatter([j],[med],color=INK,s=35,marker='_',zorder=5)
            ax.set_xticks(range(3),[NAMES[m] for m in config['methods']])
            ax.set_xlim(-.4,2.4)
            ax.set_ylim(ari_lower,1.08) if metric=='ari' else ax.set_ylim(-1.05,1.05)
            if row==0:ax.set_title(TITLES[case],color=INK,fontsize=16,pad=15)
            if col==0:ax.set_ylabel('Adjusted Rand index' if metric=='ari' else 'Silhouette score',color=INK,fontsize=12)
    count=len(config['dataset_seeds'])*len(config['init_seeds'])
    fig.text(.065,.12,f'{count} fits per method and case: {len(config["dataset_seeds"])} dataset seeds × {len(config["init_seeds"])} initialization seeds. Dots: every fit. Thick bar: IQR. White mark: median.',color=INK,fontsize=11)
    fig.text(.065,.080,'ARI uses generating labels only for evaluation; silhouette measures separation in the observed geometry. Bars are not confidence intervals.',color=MUTED,fontsize=10)
    fig.text(.065,.043,f'Actual CPU runs on synthetic data · {config["n"]} points, k = {config["k"]} · source {record["commit"][:7]} · no real-world accuracy claim',color=MUTED,fontsize=10)
    save(fig,args.output,'quality-overview')

    fig,axes=plt.subplots(2,3,figsize=(14,8.8),facecolor=BG)
    fig.subplots_adjust(left=.06,right=.97,top=.79,bottom=.18,hspace=.32,wspace=.24)
    ds=config['dataset_seeds'][0];seed=config['init_seeds'][0]
    fig.text(.06,.92,'ONE FIXED VIEW / THREE GEOMETRIES',color=INK,fontsize=25,weight='bold')
    fig.text(.06,.865,f'Preselected dataset seed {ds}, initialization seed {seed}. Top: generating components. Bottom: k-means++ assignments.',color=MUTED,fontsize=12)
    palette=ListedColormap(['#57d9c2','#ffcc80','#b6a4ff'])
    for col,case in enumerate(config['cases']):
        run=next(r for r in record['runs'] if r['case']==case and r['dataset_seed']==ds and r['init_seed']==seed and r['method']=='plus')
        with np.load(args.run/f'{case}-{ds}.npz',allow_pickle=False) as data:x,y=data['x'],data['y']
        labels=np.asarray(run['labels']);centers=np.asarray(run['centers'])
        # Colors identify clusters within each panel, not a claimed cross-panel label mapping.
        for row,values in enumerate([y,labels]):
            ax=axes[row,col];decorate(ax)
            ax.scatter(x[:,0],x[:,1],c=values,cmap=palette,vmin=0,vmax=2,s=10,alpha=.65,linewidths=0)
            ax.set_aspect('equal',adjustable='box')
            ax.set_xlabel('x₁',color=MUTED)
            if col==0:ax.set_ylabel('x₂',color=MUTED)
            if row==0:ax.set_title(TITLES[case],color=INK,fontsize=15,pad=12)
            else:
                ax.scatter(centers[:,0],centers[:,1],marker='X',s=75,c=INK,edgecolors=BG,linewidths=1,zorder=4)
                ax.set_title(f'ARI {run["ari"]:.3f} · silhouette {run["silhouette"]:.3f}',color=MUTED,fontsize=11)
    fig.text(.06,.11,'Centroid markers: white ×. Cluster colors are arbitrary IDs within each panel; colors do not imply correspondence between rows.',color=INK,fontsize=10)
    fig.text(.06,.07,'No best-run selection. The companion overview contains every planned seed; this view explains geometry rather than typical performance.',color=MUTED,fontsize=10)
    fig.text(.06,.035,f'Generated inputs, assignments and metrics loaded from the recorded experiment · source {record["commit"][:7]}',color=MUTED,fontsize=10)
    save(fig,args.output,'geometry-gallery')
    print(args.output)


if __name__=='__main__':main()
