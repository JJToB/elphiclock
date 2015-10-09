<?php
error_reporting(E_ALL);
ini_set ('display_errors', 'On');
if(!$db = new SQLite3('../wakeup.db')){
  echo "Database Connection failed";
  exit;
}

if(!$stmt = $db->prepare('SELECT id,w,h,m,active FROM times ORDER BY w,h,m;')){
  $db->exec("CREATE TABLE times (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                 w int(1),
                                 h int(2),
                                 m int(2),
                                 last int(2) DEFAULT 0,
                                 active int(1));");
  echo "Created new Database! Please reload!";
//  exit;
}

$days=array(1 => "Monday",
            2 => "Tuesday",
            3 => "Wednesday",
            4 => "Thursday",
            5 => "Friday",
            6 => "Saturday",
            0 => "Sunday");

$state=array(0 => "Off",
             1 => "On");


if(isset($_GET['set'])){
  $db->exec("UPDATE times set ".$_GET['n']."=".$_GET['v']." WHERE id=".$_GET['i'].";");
}
if(isset($_GET['add'])){
  $db->exec("INSERT INTO times (w,h,m,active) VALUES(".$_GET['w']." ,".$_GET['h']." ,".$_GET['m']." ,".$_GET['active'].");");
}
if(isset($_GET['del'])){
  $db->exec("DELETE FROM times WHERE id=".$_GET['i'].";");
}


$result = $stmt->execute();

echo "<table><tr><th>Day</th><th>Time</th><th>State</th></tr>";
while ($row = $result->fetchArray()) {
  echo "<tr".(($row['active']==1)?"":" style='color: grey;'").">"; 
  echo "<td>".$days[$row['w']]."</td><td>".sprintf("%02u:%02u",$row['h'],$row['m'])."</td>\n";
  echo "<td><a href='".$_SERVER['PHP_SELF']."?set&n=active&v=".(($row['active']==1)?"0":"1")."&i=".$row['id']."'>".$state[$row['active']]."</a></td>\n";
  echo "<td><a href='".$_SERVER['PHP_SELF']."?del&i=".$row['id']."'>[Del]</a></td>\n";
  echo "</tr>";
}
echo "</table>";
echo "<br>";
echo "<form action='".$_SERVER['PHP_SELF']."' method='get'>";
echo "Add: <select name='w'>";
foreach($days as $d=>$dn) echo "<option value='$d'>$dn</option>";
echo "</select> ";
echo "<input type='text' name='h' value='00' size='1'>:";
echo "<input type='text' name='m' value='00' size='1'>";
echo "Add: <select name='active'><option value='0'>Off</option><option value='1'>On</option></select>";
echo "<input type='submit' name='add' value='Add'></form>";

$db->close();

?>
