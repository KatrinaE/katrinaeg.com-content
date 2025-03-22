Title: Installing Unison 2.40.63 on OS X El Capitan
Date: December 27, 2015
Author: Katrina Ellison Geltman

I recently needed to install Unison version 2.40.63 on a machine running OS X
10.11 El Capitan. There are no prebuilt binaries available (except for the GUI
versions listed in "The Easy Alternative" below), so I had to install from
source. It was a bit of a pain, but I ultimately got it working successfully.
The trickiest part was figuring out which versions of Xcode and Ocaml the
build required; the actual time to tweak the source code and make the binary
was minimal.

### The Easy Alternative: Use a similar GUI version

It's possible to download [official binaries](http://unison-
binaries.inria.fr/) of the GUI versions of Unison 2.40.61 and 2.40.69. These
work out of the box, but only in GUI form - the command line tool installer
fails because of El Capitan's [System Integrity
Protection](https://support.apple.com/en-us/HT204899), which prevents writing
to /usr/bin/, even with sudo.

    
    $ sudo /Applications/Unison.app/Contents/MacOS/cltool 
    cp: /usr/bin/unison: Operation not permitted
    

### Building from Source

If you want to install the command line version or specifically need 2.40.63,
you can build from the Unison source. You'll need to install build tools and
make a couple of changes to the Unison source code before running the build
script.

#### Step 1: Installing Prerequisites

Prerequisites:

- **Xcode** (download from the [App Store](https://itunes.apple.com/us/app/xcode/id497799835?mt=12)). I used version 7.2. _Note: you need the full Xcode, not just the command line tools._
- An **OCaml compiler** (install via Homebrew; see instructions below)
- **Unison 2.40.63 source code** tarball (download 'unison-2.40.63.tar.gz' from [the official source](http://www.seas.upenn.edu/~bcpierce/unison//download/releases/unison-2.40.63/))

##### Xcode

XCode is an Apple IDE and set of SDKs. To build Unison on El Capitan you'll
need the Mac OS X El Capitan SDK, which is only available in the full version
of Xcode. The Unison Makefile also uses some XCode-specific commands.

Xcode is a large download ( > 4GB). If you're installing it for the first
time, open it once from the Applications folder so you can accept the license
agreement.

##### OCaml Compiler

Unison is written in the OCaml language, but El Capitan does not come with an
OCaml compiler. However, the OCaml package manager, OPAM, is available via
Homebrew and comes with a compiler.

    
    $ brew install opam
    

Unfortunately, OPAM's default compiler - version 4.02.3 - does not build
Unison correctly. The build will appear successful, but Unison will segfault
immediately. Fortunately, OPAM allows you to specify an alternative version
when you set it up, and to quickly switch between versions after that. The
most recent compiler version that worked for me was 4.01.0, so tell OPAM to
use that.

    
    $ opam init --comp 4.01.0
    

OPAM will ask you to let it modify `~/.bash_profile` and `~/.ocamlinit` so
that it can properly set paths and environment variables. I told it yes ("y")
to make life easier.

Once OPAM is installed, activate it and verify that it works.

    
    $ eval `opam config env`
    $ opam --version
    1.2.2
    $ ocaml -version
    The OCaml toplevel, version 4.01.0
    

###### Switching Compilers

The 4.01.0 compiler should work correctly. However, you may need to use a
different version for some reason, e.g. for compatibility with a remote Unison
installation. Fortunately, this is easy to do. For example, to switch to
version 3.12.0 of the compiler, run

    
    $ opam switch 3.12.0
    $ eval `opam config env`
    

To see all available compiler versions, use

    
    $ opam switch list
    

You'll need to rebuild Unison after you switch compilers.

##### Source Code Tarball

[Download the
tarball](http://www.seas.upenn.edu/~bcpierce/unison//download/releases/unison-2.40.63/unison-2.40.63.tar.gz).
If you'd like to keep the source code after installation, move it to wherever
you'd like to put it. (I usually use /usr/local/src).

    
    $ tar -C /usr/local/src -zxvf ~/Downloads/unison-2.40.63.tar.gz
    $ cd /usr/local/src/unison-2.40.63/
    

If, on the other hand, you're planning to delete it once the build is
complete, just leave the source code in ~/Downloads.

    
    $ cd ~/Downloads
    $ tar -zxvf unison-2.40.63.tar.gz
    $ cd unison-2.40.63
    

#### Step 2: Modifying the Source Code

The Mac OS X version is hard-coded to 10.5 in the Unison source, which
prevents it from building correctly on El Capitan. To fix it, you need to
update "10.5" to "10.11" everywhere it appears in the code. Fortunately, there
are not too many places to update:

- In **./Makefile.OCaml** , line 183
    - Old line: `MINOSXVERSION=10.5`
    - New line: `MINOSXVERSION=10.11`

- In **./uimacnew/uimacnew.xcodeproj/project.pbxproj** , lines 676, 686, and 696
    - Old line: `SDKROOT = /Developer/SDKs/MacOSX10.5.sdk;`
    - New line: `SDKROOT = /Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk;`
    - Note: this is the default location of the OS X 10.11 SDK when Xcode is installed from the Mac app store. It may be somewhere else on your system.

- In **./uimacnew09/uimacnew.xcodeproj/project.pbxproj** , lines 702, 713, and 724
    - Old line: `SDKROOT = macosx10.5;`
    - New line: `SDKROOT = macosx10.11;`

#### Step 3: Building

It's finally time to build the binary.

    
    $ cd /usr/local/src/unison-2.40.63      # Or wherever you put the source code in step 1
    $ make UISTYLE=text
    

If the build fails, clean up after it with 'make clean' before trying again:

    
    $ make clean
    

Running Unison without any arguments should bring up the help message. Note
that you'll need to run `./unison`, not `unison`, as you haven't yet placed it
on your path.

    
    $ ./unison
    Usage: unison [options]
        or unison root1 root2 [options]
        or unison profilename [options]
    
    For a list of options, type "unison -help".
    For a tutorial on basic usage, type "unison -doc tutorial".
    For other documentation, type "unison -doc topics".
    

##### Testing

Test the build locally with the directions in [the
manual](http://www.seas.upenn.edu/~bcpierce/unison//download/releases/unison-2.40.63/unison-2.40.63-manual.html#local).
Don't worry if you get a warning that begins "Warning: No archive files were
found for these roots". This is just because it's the first time you've used
Unison with these directories. Press the spacebar to continue, and make sure
the last line of output is "Nothing to do: replicas have been changed only in
identical ways since last sync.".

If you're planning to use Unison with a remote machine, you should also test
its compatibility with that machine.

##### Adding to Path

Once you're confident Unison works to your liking, you'll probably want to
copy or link it to `/usr/local/bin/unison` so that you can call it from
anywhere via `unison`.

If you're saving the source somewhere, you can use a symlink.

    
    $ ln -s /usr/local/src/unison-2.40.63/unison /usr/local/bin/unison
    

Or you can copy the binary directly. (Note: you'll have to do it this way if
you're planning to remove the source code, since the original binary is in the
source code directory).

    
    $ cp unison /usr/local/bin/unison
    

### Troubleshooting

#### Problem

You see messages that look like this:

    
    $ make UISTYLE=text
    ocamlc -o mkProjectInfo unix.cma str.cma mkProjectInfo.ml
    make: ocamlc: No such file or directory
    # [... more error output]
    

##### Solution

Install an OCaml compiler (see step 1)

#### Problem

You see lots of warnings that look like this:

    
    ld: warning: object file
    (/usr/local/lib/ocaml/libunix.a(rewinddir.o)) was built for newer OSX version (10.11) than being linked (10.5)
    

##### Solution

You need to update the source code to reference version 10.5, not 10.11 (see
step 2).

#### Problem

Unison runs, but immediately segfaults.

    
    $ ./unison
    0??Segmentation fault: 11
    

##### Solution 1

Use a different OCaml compiler (see step 1). Unison will not build on El
Capitan with OCaml 4.02.x. Try 4.01.x instead.

##### Solution 2

Make sure you've used the correct path to your OS 10.11 SDK (see step 2). If
it's not in
`/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk`,
look for it elsewhere(e.g. with mdfind).

    
    $ mdfind -name .sdk
    

#### Problem

Unison works locally, but not with a remote server. The error output contains
something like this:

    
    Fatal error: Internal error: New archives are not identical.
    

##### Solution

Recompile with an OCaml compiler that matches the one used on your remote (see
the "Switching Compilers" step above). If you don't know the remote version,
start by trying a compiler with a different major version (e.g. 3.x instead of
4.x). See also the discussion on [Stack
Exchange](http://unix.stackexchange.com/questions/52945/how-to-fix-unison-
failing-with-fatal-error-internal-error-new-archives-are-no).

* * *

###### Category: [How-to](/category/how-to.html).