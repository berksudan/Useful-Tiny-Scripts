# Example Usage: "bash ./line_count_speedometer.sh path/to/file"

file_path=$1
calc(){ awk "BEGIN { print "$*" }"; }
get_line_count() { wc -l $1 | awk '{print $1}'; }

first_line_cnt=$(get_line_count $file_path)
echo "Line Count #1: $first_line_cnt"

start_time=$(date +%s.%3N)
sleep 10;
second_line_cnt=$(get_line_count $file_path)
echo "Line Count #2: $second_line_cnt"

diff_cnt=$(($second_line_cnt-$first_line_cnt))

echo "Diff Line Count: $diff_cnt"

end_time=$(date +%s.%3N)

elapsed=$(echo "scale=3; $end_time - $start_time" | bc)
elapsed=${elapsed/./}
elapsed=$(calc $elapsed/1000)
echo "Elapsed secs: $elapsed"

echo "Line Writing Speed:" "$(calc $diff_cnt/$elapsed)" "line/s"
