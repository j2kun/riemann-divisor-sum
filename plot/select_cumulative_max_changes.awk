BEGIN {
  OFS = ","
  FS = ","
}

NR == 1 {
  print $1, $2, "cumulative_max_witness_value";
  i = 0;
  next;
}

$1 <= 9.2184 {
  next;
}

NR > 1 {
  if (i == 0) {
    the_max = $2;
  }
  
  if ($2 > the_max) {
    the_max = $2;
    print $1, $2, the_max;
  } else if (i % 500000 == 0) {
    print $1, $2, the_max;
  }

  i++;
}
