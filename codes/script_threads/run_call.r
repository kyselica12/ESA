sink(paste(opt$output, ".call", sep=""))
cat('Call:', '\n')
#cat('Rscript stars/run.r -F', opt$input,           #modified M.Zigo 20200116
cat('Rscript script_threads/run.r -F', opt$input, 
                        '-A', opt$width,
                        '-B', opt$height,
                        '-C', opt$angle,
                        '-N', opt$`noise-dim`,
                        '-L', opt$`local-noise`,
                        '-D', opt$delta,
                        '-X', opt$`start-iter`,
                        '-M', opt$`max-iter`,
                        '-I', opt$`min-iter`,
                        '-S', opt$`snr-lim`,
                        '-Z', opt$color,
                        '-E', opt$model,
                        '-O', opt$output,
                        '-Y', opt$`cent-pix-perc`,
                        '-G', opt$`init-noise-removal`,
                        '-H', opt$`fine-iter`,
                        '-K', opt$method,
                        '-P', opt$parallel,
                        '-V', opt$verbose,
                        '\n\n'
)
sink()
