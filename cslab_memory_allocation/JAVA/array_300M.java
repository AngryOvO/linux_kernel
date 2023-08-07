public class array_300M
{
	public static void main(String[] args)
	{

		System.out.println("JAVA_MEMORY_ALLOCATION");
		System.out.println("data type: int array");
		System.out.println("data size: 300000000");

		long beforeTime = System.currentTimeMillis();

		int[] a = new int [300000000];

		for(int i = 0; i < 300000000; i++)
		{
			a[i] = i;
		}

		long afterTime = System.currentTimeMillis();
		long secDiffTime = afterTime - beforeTime;

		System.out.println("process time : " + (double)secDiffTime/1000);
	}
}



