Title: Using Jupyter notebooks securely on remote linux machines
Date: 2015-12-18
Category: Tips
Tags: data, AWS, jupyter, python

There are times when it makes sense to offload work from a local laptop to a remote machine. When the data set already resides in AWS it's much faster to download it to an EC2 instance rather than to your machine. Occasionally a bit more RAM or disk space is needed, a problem easily solved by spinning up a high end instance. In this post I'll show how I use [Jupyter notebooks](http://jupyter-notebook.readthedocs.org/en/latest/index.html) on remote linux machines, typically AWS EC2 instances.

I don't use the built in notebook server feature. I don't feel comfortable exposing *all* the privileges of my account behind a single password on a webpage (anyone who accesses the Jupyter notebook server can run arbitrary code as your user). My method is to run the standard server that only listens to *localhost* with an ssh tunnel to securely connect.

## 1. Setting up the remote linux machine

1. Launch an AWS EC2 instance (see [this page](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance_linux.html) for help). I usually launch a spot instance for lower cost.
1. SSH into the instance. All the commands below should be run on the remote machine.
1. [Install anaconda](http://docs.continuum.io/anaconda/install#linux-install). The below commands work as of now, but the link may change in the future (I got the location from the [anaconda downloads page](https://www.continuum.io/downloads)).

        :::console
        wget https://3230d63b5fc54e62148e-c95ac804525aac4b6dba79b00b39d1d3.ssl.cf1.rackcdn.com/Anaconda2-2.4.1-Linux-x86_64.sh
        # follow the prompts, answer "yes" to the question about prepending the path
        bash Anaconda2-2.4.1-Linux-x86_64.sh
        # need to update PATH for this session
        source ~/.bashrc

1. Start `tmux`, which will allow your notebook server to continue to run even after you log out. I do all my terminal work within [tmux (Terminal Multiplexer)](https://tmux.github.io/) and I highly recommend learning to use it.

        :::console
        tmux

1. Start jupyter notebook within your tmux session. The `--no-browser` option prevents jupyter from automatically opening a browser window.

        :::console
        jupyter notebook --no-browser

## 2. Connecting to the remote notebook server

The next step is to use an SSH tunnel to forward a port on your local machine to the remote machine. You can think of this as connecting port 8157 on your local machine to port 8888 (the default jupyter notebook port) on the remote machine.

    :::console
    # run from your local machine
    ssh -i /path/to/ssh/key -NL 8157:localhost:8888 ubuntu@your-remote-machine-public-dns

You should now be able to point your browser to `http://localhost:8157` and see the jupyter notebook startup screen.

## 3. Saving your work locally

I like to automatically save my notebooks locally so I don't lose any work. The method uses `rsync` and will sync notebooks every 30 seconds.

1. I have the following lines in my `~/.ssh/config` file, which allows all of the instances of `"ubuntu@your-remote-machine-public-dns"` above to be replaced by `"tmpaws"`. I paste the dns of the machine I'm working on into this file each time it changes.

        :::text
        Host tmpaws
        	HostName your-remote-machine-public-dns
        	User ubuntu
        	IdentityFile /path/to/ssh/key

1. Run the below command to continually sync your notebooks. It's an eyesore but the least cumbersome option I've found.

        :::console
        while true; do \
         rsync -avz --include='*.ipynb' --exclude='*' tmpaws:/path/to/notebooks/ /path/to/local/dir/; \
         sleep 30; \
        done

1. As always, keep your local copy of the notebooks under version control.

## 4. The result

<img src="/extra/images/remote-notebook.png" title="remote-notebook" style="display: block; border: 3px solid grey;">
