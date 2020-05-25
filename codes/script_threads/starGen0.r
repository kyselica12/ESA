# Rscript script/starGen.r -F fits/test -X 1024 -Y 1024 -N 2000 -A 0.5 -B 1 -C 700 -D 20000 -M cauchy -G 100 -S 30
# pouzivanie
# -F kam sa ulozi fits subor (zadava sa bez pripony fits), pdf-ka aj tablka s hviezdami sa ulozi do adresara odkial si skript spustil
# -X pocet stlpcov
# -Y pocet riadkov
# -N pocet hviezd
# -A min
# -B max hodnota sirky hviezdy (pre gauss je to stdev, pre cauchy je to hodnota gamma)
# -C min jasnost
# -D max jasnost
# -M metoda (gauss, cauchy)
# -G stredna hodnota sumu pozadia
# -S odchylka sumu pozadia


library(FITSio)
library(optparse)

option_list = list(
# used: ACDGHILMNOPWSXY
    make_option(c("-O", "--output"), 
                type    = "character", 
                default = NULL, 
                help    = "Output FITS file (path + name without extension .fits)"),
                
    make_option(c("-I", "--input"), 
                type    = "character", 
                default = NULL, 
                help    = "Input *.cat file with stars."),
                
    make_option(c("-H", "--header"), 
                type    = "character", 
                default = NULL, 
                help    = "FITS file that will be used for header."),
                
    make_option(c("-X", "--dimX"), 
                type    = "numeric", 
                default = 1024, 
                help    = "Number of columns (default 1024)"),
                
    make_option(c("-Y", "--dimY"), 
                type    = "numeric", 
                default = 1024, 
                help    = "Number of rows (default 1024)"),
                
    make_option(c("-P", "--prec"), 
                type    = "numeric", 
                default = 3, 
                help    = "Grid density of a pixel for star generation (default 3)"),
                
    make_option(c("-N", "--starCount"), 
                type    = "integer", 
                default = 1000, 
                help    = "Number of generated stars (default 1000)"),
                
    make_option(c("-W", "--fwhm"), 
                type    = "numeric", 
                default = 3, 
                help    = "Full width at half maximum (default 3)"),
                
#    make_option(c("-B", "--spreadMax"), 
#                type    = "numeric", 
#                default = NULL, 
#                help    = "max value of star width"),
#                
    make_option(c("-C", "--briMin"), 
                type    = "numeric", 
                default = 1000, 
                help    = "Min brightness (default 1000)"),
                
    make_option(c("-D", "--briMax"), 
                type    = "numeric", 
                default = 10000, 
                help    = "Max brightness (default 10000)"),
                
    make_option(c("-M", "--method"), 
                type    = "character", 
                default = "gauss", 
                help    = "Method: gauss, cauchy (default gauss)"),
                
    make_option(c("-G", "--gaussM"), 
                type    = "numeric", 
                default = 100, 
                help    = "Mean value of background noise (default 100)"),
                
    make_option(c("-S", "--gaussS"), 
                type    = "numeric", 
                default = 30, 
                help    = "Stdev of gackground noise (default 30)"),
                
    make_option(c("-L", "--lines"), 
                type    = "numeric", 
                default = 0, 
                help    = "Generate lines (N -- length in multiples of STDEV) instead of points (0) for stars (default 0)"),
                
    make_option(c("-A", "--alpha"), 
                type    = "numeric", 
                default = 0, 
                help    = "Slope of lines (default 0)")
)

opt_parser = OptionParser(option_list=option_list)
opt = parse_args(opt_parser)

# params
method    = opt$method
prec      = opt$prec
dimX      = opt$dimX*prec
dimY      = opt$dimY*prec
starCount = opt$starCount
briMin    = opt$briMin
briMax    = opt$briMax
backMean  = opt$gaussM
backSdev  = opt$gaussS

if(!is.null(opt$header)){
    header = readFITS(opt$header)$header
}else{
    header = ''
}


parseCat = function(input){
    X = c()
    Y = c()
    F = c()
    W = c()
    alldata = readLines(input)
    for(i in 4:length(alldata)){
        l = gsub("^ *|(?<= ) | *$", "", alldata[i], perl = TRUE)
        p = strsplit(l, ' ')[[1]]
        if(length(p) != 17){
            next
        }
        X = c(X, as.numeric(p[12]))
        Y = c(Y, as.numeric(p[13]))
        F = c(F, as.numeric(p[14]))
        W = c(W, as.numeric(p[15]) / 1.67)
    }
    return(list(
        'X' = X,
        'Y' = Y,
        'F' = F,
        'W' = W))
}

switchX = function(F){
    return(apply(t(F[,ncol(F):1]),2,rev))
}

# bivariate gaussian
bigauss  = function(x,y,k,sgx2,sgy2) k*exp(-0.5*(x**2/sgx2 + y**2/sgy2))
print(bigauss)
# bivariate cauchy
bicauchy = function(x,y,k,g2) k / (x**2 + y**2 + g2)**1.5

genStarGauss = function(star.x,star.y,bri,sgx,sgy){
    
    # x,y is a position of the star
    # bri is the birghtness of the whole object (ie, sum of its pixels)
    
    k = 1/2/pi/sgx/sgy
    sgx2 = sgx**2
    sgy2 = sgy**2
    limX = ceiling(5*sgx)
    limY = ceiling(5*sgy)
    
    # rows/y coordinates (upy <= y <= dwy) ... matrix orientation: TL = (1,1), BR = (dimX,dimY)
    upy =   floor(max(1,    star.y - limY))
    dwy = ceiling(min(dimY, star.y + limY))
    # cols/x coordinates (upx <= x <= dwx)
    upx =   floor(max(1,    star.x - limX))
    dwx = ceiling(min(dimX, star.x + limX))

    for(y in upy:dwy){ # rows
        for(x in upx:dwx){ # cols
            FITS[y,x] <<- FITS[y,x] + bri*bigauss(star.x - x, star.y - y, k, sgx2, sgy2)
        }
    }

    return(0)
}

genStarCauchy = function(star.x,star.y,bri,gam){
    
    # bri is the birghtness of the whole object
    
    k    = gam / 2 / pi
    gam2 = gam**2
    limX = 5*gam
    limY = 5*gam
    
    # rows/y coordinates (upy <= y <= dwy) ... matrix orientation: TL = (1,1), BR = (dimX,dimY)
    upy =   floor(max(1,    star.y - limY))
    dwy = ceiling(min(dimY, star.y + limY))
    # cols/x coordinates (upx <= x <= dwx)
    upx =   floor(max(1,    star.x - limX))
    dwx = ceiling(min(dimX, star.x + limX))
    
    for(y in upy:dwy){ # rows
        for(x in upx:dwx){ # cols
            FITS[y,x] <<- FITS[y,x] + bri*bicauchy(star.x - x, star.y - y, k, gam2)
        }
    }
    
    return(0)
}

genLineGauss = function(star.x,star.y,bri,stdev,wid,alpha){
    # x,y is a position of the star
    # bri is the birghtness of the whole object (ie, sum of its pixels)
    # wid is the width of the plateua in units of stdev

    
            # check on which side of line a point (x,y) lies (in the direction of the line given by points A,B)
            
            checkRight = function(x,y,A,B){
                x1 = A[1]
                y1 = A[2]
                x2 = B[1]
                y2 = B[2]
                return((x - x1)*(y2 - y1) - (y - y1)*(x2 - x1) >= 0)
            }
#
            checkLeft  = function(x,y,A,B){
                x1 = A[1]
                y1 = A[2]
                x2 = B[1]
                y2 = B[2]
                return((x - x1)*(y2 - y1) - (y - y1)*(x2 - x1) <= 0)
            }
#
            getCorners = function(C.X,C.Y,A,B){
                # corners of a box with centre C and half-length A and B
                # basic vectors of the box
                vecR = c(C.X, C.Y)
                vecA = c(A*cos(alpha), A*sin(alpha))
                vecB = c(B*cos(alpha+pi/2), B*sin(alpha+pi/2))
                
                # four corners of the box
                TL = vecR - vecA + vecB
                TR = vecR + vecA + vecB
                BL = vecR - vecA - vecB
                BR = vecR + vecA - vecB
                
                # define four bounding lines
                if(abs(tan(alpha)) > 0){
                    tgA  = tan(alpha)
                    tgA2 = tan(alpha + pi/2)
                    L1 = c(tgA,  -1, TR[2] - tgA *TR[1])
                    L2 = c(tgA,  -1, BL[2] - tgA *BL[1])
                    L3 = c(tgA2, -1, BL[2] - tgA2*BL[1])
                    L4 = c(tgA2, -1, TR[2] - tgA2*TR[1])
                }else{
                    L1 = c(0, 1, -TR[2])
                    L2 = c(0, 1, -BL[2])
                    L3 = c(1, 0, -BL[1])
                    L4 = c(1, 0, -TR[1])
                }
                
                # define box pixel borders (four lines perpendicular to axes and passing through box four corners)
                box.top = floor  (max(TL[2], TR[2], BL[2] ,BR[2]))   # first horizontal line from the top to cut the box
                box.bot = ceiling(min(TL[2], TR[2], BL[2] ,BR[2]))   # first horizontal line from the bottom to cut the box 
                box.lef = ceiling(min(TL[1], TR[1], BL[1] ,BR[1]))
                box.rig = floor  (max(TL[1], TR[1], BL[1] ,BR[1]))
            
                return(list('top' = box.top, 'bot' = box.bot, 'lef' = box.lef, 'rig' = box.rig))
            }
#
            projectPnt = function(P,A,B){
                # project point P onto line given by points A and B
                
                dot = function(a,b) sum(a*b)
                
                AP = P - A
                AB = B - A
                return(A + dot(AP,AB)/dot(AB,AB)*AB)
            }
#
    
    centre = c(star.x, star.y)
    
    shift  = wid * stdev * c(cos(alpha), sin(alpha))
    
    rightP = centre + shift
    leftP  = centre - shift
    
    k = 1/2/pi/stdev/stdev
    stdev2 = stdev**2
    
    corners = getCorners(stdev*wid + 5*stdev, 5*stdev)
    # rows/y coordinates (upy <= y <= dwy) ... matrix orientation: TL = (1,1), BR = (dimX,dimY)
    upy = corners$top
    dwy = corners$bot
    # cols/x coordinates (upx <= x <= dwx)
    upx = corners$lef
    dwx = corners$rig

    upy =   floor(max(1,    star.y - limY))
    dwy = ceiling(min(dimY, star.y + limY))
    # cols/x coordinates (upx <= x <= dwx)
    upx =   floor(max(1,    star.x - limX))
    dwx = ceiling(min(dimX, star.x + limX))

    for(y in upy:dwy){ # rows
        for(x in upx:dwx){ # cols
            alpha2 = alpha + pi/2
            SIN = sin(alpha2)
            COS = cos(alpha2)
            if(checkLeft(x, y, leftP, leftP + c(COS, SIN))){
                FITS[y,x] <<- FITS[y,x] + bri*bigauss(star.x - x, star.y - y, k, stdev2, stdev2)
            }else{
            if(checkRight(x, y, rightP, rightP + c(COS, SIN))){
                FITS[y,x] <<- FITS[y,x] + bri*bigauss(star.x - x, star.y - y, k, stdev2, stdev2)
            }else{
                # this is the strechted zone
                # project point on the left line
                projected = projectPnt(c(x,y), leftP, leftP + c(COS, SIN))
                FITS[y,x] <<- FITS[y,x] + bri*bigauss(star.x - projected[1], star.y - projected[2], k, stdev2, stdev2)
            }}
        }
    }

    return(0)
}

if(is.null(opt$input)){
    # coordinates
    coordx = runif(starCount, 1, dimX)
    coordy = runif(starCount, 1, dimY)

    # brightness
    bri = runif(starCount, briMin, briMax)

    # star size
    if(method == 'gauss'){
        sgx = rep(opt$fwhm / 2.355, starCount)
        sgx = sgx*prec
        sgy = sgx
    }else{
        gam = rep(opt$fwhm / 2, starCount)
        gam = gam * prec
    }
}else{
    
    input = parseCat(opt$input)
    
    cat('Parsed '); cat(as.character(length(input$X))); cat(' stars\n')
    
    starCount = length(input$X)
    
    # coordinates
    coordx = input$X*prec
    coordy = input$Y*prec

    # brightness
    bri = input$F

    # star size
    if(method == 'gauss'){
        sgx = input$W / 2.355
        sgx = sgx*prec
        sgy = sgx
    }else{
        gam = input$W / 2
        gam = gam * prec
    }
}

# generate FITS
cat("Generating stars\n")
FITS = matrix(0, nrow=dimY, ncol=dimX)
if(opt$lines > 0){
    for(i in 1:starCount){
        genLineGauss(coordx[i], coordy[i], bri[i], sgx[i], opt$lines, opt$alpha)
    }
}else{
if(method == 'gauss'){
    for(i in 1:starCount){
        genStarGauss(coordx[i], coordy[i], bri[i], sgx[i], sgy[i])
    }
}else{
    for(i in 1:starCount){
        genStarCauchy(coordx[i], coordy[i], bri[i], gam[i])
    }
}}


# write model - transform coordinates to original pixels
cat("Writing star table (model.tsv)\n")
model = cbind(coordx/prec, coordy/prec, bri)
colnames(model) = c('model.x', 'model.y', 'max.brightness')
write.table(model[order(model[,1]),], 'model.tsv', col.names=F, row.names=F, sep='\t')

# reduce to original size
if(prec > 1){
    cat("Reducing enahanced image\n")
    dimX = opt$dimX
    dimY = opt$dimY
    FITS_fin = matrix(0, nrow=dimY, ncol=dimX)
    for(y in 1:dimY){
        for(x in 1:dimX){
            y1 = (y-1)*prec + 1
            y2 = y*prec
            x1 = (x-1)*prec + 1
            x2 = x*prec
            FITS_fin[y,x] = sum(FITS[y1:y2,x1:x2])
        }
    }
    
    FITS = FITS_fin
}

# write model pdf
cat("Writing star image (model.pdf)\n")
pdf('model.pdf', height=10, width=10)
image(1:ncol(FITS), 1:nrow(FITS), t(FITS), col = grey(seq(0, 1, length = 65535)), axes = FALSE)
invisible(dev.off())

# generate poisson noise
cat("Generating Poisson noise\n")
for(x in 1:dimX){
    for(y in 1:dimY){
        FITS[x,y] = rpois(1, FITS[x,y])
    }
}

cat("Writing star FITS file ("); cat(paste(getwd(),'/',opt$output, '_stars.fits)\n', sep=''))
writeFITSim(switchX(FITS), file = paste(opt$output, '_stars.fits', sep=''), type = "single", 
            bscale = 1, bzero = 0, c1 = NA, c2 = NA, crpixn = NA, crvaln = NA, cdeltn = NA, ctypen = NA, cunitn = NA, axDat = NA, 
            header = header)


# generate gaussian background noise
cat("Generating Gaussian noise\n")
noise = matrix(abs(rnorm(dimX*dimY, mean=backMean, sd=backSdev)), nrow=dimY, ncol=dimX)
cat("Writing Gaussian noise (noise.pdf)\n")
pdf('noise.pdf', height=10, width=10)
image(1:ncol(noise), 1:nrow(noise), t(noise), col = grey(seq(0, 1, length = 65535)), axes = FALSE)
invisible(dev.off())

cat("Writing noise FITS file ("); cat(paste(getwd(),'/',opt$output, '_noise.fits)\n', sep=''))
writeFITSim(switchX(noise), file = paste(opt$output, '_noise.fits', sep=''), type = "single", 
            bscale = 1, bzero = 0, c1 = NA, c2 = NA, crpixn = NA, crvaln = NA, cdeltn = NA, ctypen = NA, cunitn = NA, axDat = NA, 
            header = header)


FITS = FITS + noise

makePosit = function(X){
    X[X < 0] = 0
}

FITS = makePosit(X)

cat("Writing final image (stars.pdf)\n")
pdf('stars.pdf', height=10, width=10)
image(1:ncol(FITS), 1:nrow(FITS), t(FITS), col = grey(seq(0, 1, length = 65535)), axes = FALSE)
invisible(dev.off())

# write FITS
cat("Writing FITS file ("); cat(paste(getwd(),'/',opt$output, '.fits)\n', sep=''))
writeFITSim(switchX(FITS), file = paste(opt$output, '.fits', sep=''), type = "single", 
            bscale = 1, bzero = 0, c1 = NA, c2 = NA, crpixn = NA, crvaln = NA, cdeltn = NA, ctypen = NA, cunitn = NA, axDat = NA, 
            header = header)

cat('Done\n')
