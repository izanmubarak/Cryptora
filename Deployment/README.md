# Hosting Cryptora 

This document provides some guidance on how to host Cryptora on your local machine, on Amazon Web Services (AWS), OpenShift, and PythonAnywhere.

These days, Cryptora is hosted on Amazon Web Services. Before that, it was hosted on OpenShift for almost a year (before their change in service offerings severely limited the free tier), and for a brief period of time, on PythonAnywhere.

## The `tokens.txt` file

Hosting Cryptora – locally or on a server platform such as AWS – requires you to generate a `tokens.txt` file which contains two token strings: the token that Telegram generated for you when you created your bot through BotFather, and the token that CoinMarketCap generates for you in order for you to use their API. In this folder, you'll see a `tokens_sample.txt` file that you can use as a template, but the format for `tokens.txt` is below:

`CMC_TOKEN==Your_CMC_API_token_here`
`BOT_TOKEN==Your_BotFather_token_here`

You need only copy and paste the respective tokens after `CMC_TOKEN==` and `BOT_TOKEN==`. Do not put quotation marks or anything around the tokens. Also, ensure that there is **no newline** at the end of the file - this will throw errors when you attempt to run the program! Some text editors add a newline automatically - you can simply run `truncate -s -1 tokens.txt` in Terminal to remove it.

Make sure that `tokens.txt` is in the root Cryptora folder, not the "Deployment" folder that `tokens_sample.txt` is in.

## Locally hosting Cryptora

Once you have created your `tokens.txt` file and placed it in the root Cryptora folder, you can start the bot by typing `python app.py`. The bot will automatically retrieve and use the tokens from the `tokens.txt` file if you have provided valid tokens. If it doesn't, you may get a `KeyError` saying that the bot cannot find a `[data]` dictionary (this is usually if you have provided an invalid CoinMarketCap API token). python-telegram-bot will throw a self-explanatory error if you provide an invalid bot token.

The bot will run indefinitely within Terminal, until you force stop it (Ctrl-C) or the computer sleeps for some reason.

## Hosting Cryptora on AWS

Hosting Cryptora on AWS is a much more involved affair, but you can use Docker to make the process significantly easier. Docker will create a container based on Ubuntu that you can run Cryptora in. As AWS servers support Docker, this approach requires far less effort than manually installing everything.

If you choose to use Docker, the `Dockerfile` in this folder will automate the majority of the setup process. It automatically installs Python 2.7, git, and pip, downloads Cryptora from this repository, and installs all of its dependencies (which are written in `requirements.txt`) onto a Docker image that you can create a container from. 

On the AWS Console, create a new EC2 Micro instance (this is part of the AWS Free Tier, so you don't need to pay to use Amazon's servers). Generate your RSA private key and keep it safe. Make sure that you select `Amazon Linux 2 AMI (HVM), SSD Volume Type` - this is a special version of Linux that the server will run. In the following options, pick everything that is "Free tier eligible." Create a new key pair if you don't have one, and save it somewhere safe. Launch the instance once you are finished.

Click "Instances" option in the sidebar if you are not there already. Click "Connect" to establish an SSH connection to the AWS server, and follow the instructions to establish an SSH connection into your instance using a terminal (make sure to have the key pair you generated previously on hand). Once you have established an SSH connection, follow [these instructions from Amazon](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html) to install and start the Docker service on your EC2 instance.

Following this, use `scp` and the key pair you generated to securely copy the `Dockerfile` to your EC2 instance. Create a new image from this Dockerfile, and then create a container from that image. Start the container and you will see all of the Cryptora files in your container already. The last thing you need to do is generate your `tokens.txt` file - refer to the first section in this document on how to do this.

Once this is done, you can just run `python app.py` to start up Cryptora. You should be able to exit your Terminal and the bot should still run.

## Hosting Cryptora on OpenShift

Cryptora was once hosted on OpenShift, but a change in their service offerings made it so that you can't indefinitely run a free server - you have to renew it every 60 days, unless you choose one of their paid options. Hosting Cryptora on OpenShift is still possible, but with the main caveat that you cannot (as far as I know) add a `tokens.txt` file to your server after the fact - it needs to be in your git repository, as OpenShift actually connects directly to a GitHub repository. To get around this, you can fork this repository, add your `tokens.txt` file to your fork, and follow the setup process that OpenShift has for Python apps. Once you have it running, you can set your forked repository to "Private" on GitHub, so that your tokens are not exposed to the public. If you wish to make any changes to your fork, you have to set the repository to "Public", make the changes, and then set it back to "Private."

## Hosting Cryptora on PythonAnywhere

PythonAnywhere is another option that you can explore to host Cryptora, but the free tier will often stop the Cryptora process randomly and you will need to restart it approximately once a day. As far as I know, the paid tier does not have this limitation. If you choose PythonAnywhere, the process is significantly easier than OpenShift or AWS. Download this repository, create your `tokens.txt` file, and upload these files to your PythonAnywhere account. Then, you can use the browser-based interactive terminal to start the program. In the `Tasks` option on PythonAnywhere, you can designate the program to be an "Always-On Task", but this is another feature only available to paid accounts.
