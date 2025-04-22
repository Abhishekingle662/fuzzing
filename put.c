#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include <zlib.h>

int main()
{
	uint8_t buf[8] = {0, };
#ifdef CHECK_CRC32
	uint32_t crc32_input;
	ssize_t r0 = read(STDIN_FILENO, &crc32_input, sizeof(uint32_t));
	if (r0 != sizeof(uint32_t))
		return 0;
#endif
	ssize_t r = read(STDIN_FILENO, buf, sizeof(buf));
	if (r < 3)
		return 0;
#ifdef CHECK_CRC32
	if (crc32(crc32(0L, Z_NULL, 0), buf, r) != crc32_input)
		return 0;
#endif
	if (buf[0] == 'U')
	{
		void** p = malloc(sizeof(void*));
		if (buf[1] == 'A')
		{
			free(p);
			if (buf[2] == 'F')
			{
				printf("%p\n", *p);
			}
		}
	}
	return 0;
}