# sudo apt-get install r-base-dev libssl-dev libcurl4-openssl-dev python-dev python3-dev python-pandas python3-pandas

options(width=160)
options(digits=6)

pkgCall = function(x) suppressWarnings(suppressMessages(suppressPackageStartupMessages(invisible(require(x,character.only = TRUE)))))
pkgInst = function(x) suppressWarnings(suppressMessages(suppressPackageStartupMessages(invisible(install.packages(x,dep=TRUE)))))
pkgTest = function(x){
    cat('Loading package', x, '\n')
    if(!pkgCall(x)){
     cat('  Package',x,'not installed, trying to install ...\n')
     pkgInst(x)
     if(!pkgCall(x)) stop("  Package not found")
    }
}

cat('\n')

pkgTest("parallel")
pkgTest("dplyr")
pkgTest("FITSio")
pkgTest("ggplot2")
pkgTest("scales")
pkgTest("tidyr")
pkgTest("ggplot2")
pkgTest("grid")
pkgTest("jpeg")
pkgTest("optparse")
pkgTest("spatstat")
pkgTest("car")
# pkgTest("rPython")

cat('\n')

# functions
cat('Loading source file script/getPixels.r\n');     source('script_threads/getPixels.r')
cat('Loading source file script/gravityCentre.r\n'); source('script_threads/gravityCentre.r')
cat('Loading source file script/wrapper.r\n');       source('script_threads/wrapper.r')
cat('Loading source file script/database.r\n');      source('script_threads/database.r')
cat('Loading source file script/report.r\n');        source('script_threads/report.r')

cat('\n')
