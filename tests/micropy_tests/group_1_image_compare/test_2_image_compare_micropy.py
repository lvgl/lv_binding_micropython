
start_time = time.time_ns()

left_over = 0
while True:
    curr_time = time.time_ns()
    new_amount = time.ticks_diff(start_time, curr_time) + left_over
    new_amount = abs(new_amount)
    left_over = new_amount & 0x3E8
    new_amount >>= 12
    new_amount = abs(new_amount)
    
    if new_amount:
        lv.tick_inc(new_amount)
        lv.task_handler()
        start_time = curr_time

# end
