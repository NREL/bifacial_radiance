BEGIN { sum=0; count =0; }
      { sum=sum+$3; count=count+1 }
END   {printf " %f\n",sum/count; }
