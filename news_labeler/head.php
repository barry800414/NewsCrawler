<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>

<link rel="stylesheet" href="./bootstrap.min.css" />
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.1/js/bootstrap.min.js"></script>
<nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="./intro.php">Agreement Prediction</a>
        </div>
    <div id="navbar" class="collapse navbar-collapse">
        <ul class="nav navbar-nav">
        <li><a href="./annotate.php">Annotation Page</a></li>
        <li><a href="./contact.php">Contact</a></li>
        </ul>

        <ul class="nav navbar-nav navbar-right">
        <?php     
            if(session_id() == '') {
                session_start();
            }   
            if(!isset($_SESSION['valid_user'])){ 
                echo '<li><a href="register.php">Register</a></li>';
			    echo '<li><a href="login.php">Login</a></li>';
		    }
            else{ 
                echo "<li><a> Hello, ".$_SESSION['valid_user']."</a></li>";
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
