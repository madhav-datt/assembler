main:
	addi $sp, $sp, 128
	addi $a0, $0, 8 # n = 8
	addi $s3, $0, 1
	addi $s4, $0, 2
	jal fib
	add $s0, $v0, $0
	j done

fib:
	addi $sp, $sp, -20
	sw $ra, 20($sp)
	beq $a0, $s3, n0
	beq $a0, $s4, n1
	
	sw $a0, 0($sp)
	lw $t0, 0($sp)
	
	addi $t1, $t0, -1
	addi $t2, $t0, -2
	
	sw $t1, 4($sp)
	sw $t2, 8($sp)
	
	lw $a0, 4($sp)
	jal fib
	sw $v0, 12($sp)
	
	lw $a0, 8($sp)
	jal fib
	sw $v0, 16($sp)
	
	lw $t3, 12($sp)
	lw $t4, 16($sp)
	
	add $v0, $t3, $t4
	j end

n0:
	# Fibonacci base case n = 1
	addi $v0, $0, 0
	j end

n1:
	# Fibonacci base case n = 2
	addi $v0, $0, 1
	j end

end:
	# End of fibonacci function
	lw $ra, 20($sp)
	addi $sp, $sp, 20
	jr $ra

done:
	# Result from fib function -> $s0 = 13
	ori $t6, $0, 1
	addi $s1, $s0, 1
	j while
	
while:
	# Do while loop with exit condition $s1 = 0
	addi $s1, $s1, -1
	add $s5, $s5, $s4  # $s5 = $s5 + 2
	bne $s1, $0, while
	
