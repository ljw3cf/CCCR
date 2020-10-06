//Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.
//PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-developer-guide/blob/master/LICENSE-SAMPLECODE.)

// Starter class. Use to create a StreamManager class
// and call stream processor operations.
package com.amazonaws.samples;
import com.amazonaws.samples.*;

public class starter {

	public static void main(String[] args) {
		
		
    	String streamProcessorName="test-StreamProcessor";
    	String kinesisVideoStreamArn="arn:aws:kinesisvideo:ap-northeast-1:670205369612:stream/video-test/1601013014959";
    	String kinesisDataStreamArn="arn:aws:kinesis:ap-northeast-1:670205369612:stream/test-datastream";
    	String roleArn="arn:aws:iam::670205369612:role/rekognition";
    	String collectionId="Collection ID";
    	Float matchThreshold=50F;

		try {
			StreamManager sm= new StreamManager(streamProcessorName,
					kinesisVideoStreamArn,
					kinesisDataStreamArn,
					roleArn,
					collectionId,
					matchThreshold);
			//sm.createStreamProcessor();
			//sm.startStreamProcessor();
			//sm.deleteStreamProcessor();
			//sm.deleteStreamProcessor();
			//sm.stopStreamProcessor();
			//sm.listStreamProcessors();
			//sm.describeStreamProcessor();
		}
		catch(Exception e){
			System.out.println(e.getMessage());
		}
	}
}
