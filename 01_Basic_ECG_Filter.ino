void setup() {
  // put your setup code here, to run once:
  
  pinMode(13,INPUT);
  pinMode(12,INPUT);
  Serial.begin(9600);
 
}
  const int pencereboyutu= 10;
  int datas[pencereboyutu];
  int index=0;
  long toplam=0;
//we write our variables for global if u write in setup, loop wont be able to see ur variables

void loop() {
  // put your main code here, to run repeatedly:

  //security control
  if(digitalRead(13)==HIGH || digitalRead(12)==HIGH){
    Serial.println("peds are out of the body, no signal!");
    delay(10);
    return; //return cuts the all loop dont continue after this dont go down
} 
  int rawsignal=analogRead(A0);

  toplam=toplam-datas[index];
  //get out the oldest data from the summation
  datas[index]= rawsignal;
  //read new data write it instead of oldest data
  toplam=toplam+datas[index];
  //add new data to summation
  index=index+1;

  if(index>= pencereboyutu){
    index=0;
  }
  //for making index <10 

  int ortalama=toplam/pencereboyutu;

  Serial.print("raw");
  Serial.print(rawsignal);
  Serial.print(" ");
  Serial.print("filtered");
  Serial.println(ortalama);
  //to continue from next row use ln
  
  delay(10);

}
