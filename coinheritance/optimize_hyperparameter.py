import os
def option_parser():
    from optparse import OptionParser
    usage = """
        THIS IS CO-INHERITANCE 1.0.0
        python optimize_hyperparameter.py --target ../test_data/target_genomes --gene ../test_data/seqs.faa --outdir ../results 
        """
    description = """CO-INHERTITANCE is a tool to compute co-inheritance relationship for a set of genes.
                    Methods is by this paper:
                    Shin J, Lee I. Co-Inheritance Analysis within the Domains of Life Substantially Improves Network Inference by Phylogenetic Profiling. 
                    PLoS One. 2015;10(9):e0139006. Published 2015 Sep 22. doi:10.1371/journal.pone.0139006
                    This script computes the mutual information/normalized mutual information based on pivot table (output by diamond_to_pivot.py)
                """

    parser = OptionParser(usage=usage, description=description)
    parser.add_option("-p", "--pool", dest="pool", type = "int", default = 8,
                  help="number of multiprocessing threads")
    parser.add_option("-t", "--target",dest="target",
                  help="path to target genomes")
    parser.add_option("-g", "--gene",dest="query",
                  help="path to .faa for query sequences")
    parser.add_option("-o", "--outdir",dest="outdir", default = '/tmp', type = "string",
                  help="output directory")
    parser.add_option("-d", "--diamond",dest="run_diamond", default = 0, type = "int",
                  help="run diamond from scratch")
    
    


    (options, args) = parser.parse_args()   

    return options

if __name__=='__main__':
    options = option_parser()

    diamond_out = os.path.join(options.outdir, 'diamond_results')
    if options.run_diamond == 1:
        # run diamond
        for faa in [f for f in os.listdir(options.target) if f.endswith('.faa')]:
            full_faa_path = os.path.join(options.target, faa)
            full_dmnd_path = os.path.join(options.target, faa.replace('.faa', ''))
        
            os.system('diamond makedb --in {} --db {} --quiet'.format(full_faa_path, full_dmnd_path))

        
        try:
            os.mkdir(diamond_out)
        except:
            print('Already exists : {}'.format(diamond_out))
    
        for dmnd in [f for f in os.listdir(options.target) if f.endswith('.dmnd')]:
            full_dmnd_path = os.path.join(options.target, dmnd)
            dmnd_result = os.path.join(diamond_out, dmnd.replace('.dmnd', ''))
            os.system('diamond blastp --query {} --db {} --out {} --outfmt 6 qseqid evalue --threads 8 --quiet'.format(
                options.query, full_dmnd_path, dmnd_result))
        print('Done with diamond')
    
    dir_path = os.path.dirname(os.path.realpath(__file__))
    

    ############# Try different bins ##################
    

    for b in [10,50,100, 150,200]:

        bindir = os.path.join(options.outdir, str(b))
        try:
            os.mkdir(bindir)
        except:
            pass

        fullpath = os.path.join(dir_path, 'diamond_to_pivot.py')
        os.system('python {} -r {} -d {} -o {} -b {}'
        .format(fullpath, options.query,diamond_out,bindir, b
        ))
    
        fullpath = os.path.join(dir_path, 'cal_score_async.py')
        npz = os.path.join(bindir, 'binned.pivot.npz')

        for s in ['mutual_info', 'normalized_mutual_info']:

            os.system('python {} --table {} -o {} --score {}'
            .format(fullpath, npz ,bindir, s
            ))

            print('Done with {} {}'.format(s,b))
    
    
    #python cal_score.py --table $outdir/binned.pivot.npz -o $outdir --score $score


