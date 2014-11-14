<link rel="stylesheet" href="./bootstrap.min.css" />
<nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="./annotate.php">Agreement Prediction</a>
        </div>
    <div id="navbar" class="collapse navbar-collapse">
        <ul class="nav navbar-nav">
        <li class="active"><a href="./annotate.php">Annotation Page</a></li>
        <li><a href="./contact.php">Contact</a></li>
        </ul>

        <ul class="nav navbar-nav navbar-right">
        <?php     
		    session_start();
		    if(!isset($_SESSION['valid_user'])){ 
			    echo '<li><a href="login.php">Login</a></li>';
		    }
		    else{ 
			    echo '<li><a href="logout.php">Logout</a></li>';
		    }   
	    ?>
        </ul>
    </div><!--/.nav-collapse -->
</nav>

<div id="head_bar">
	<div id="user_bar">
		</div>
</div>
