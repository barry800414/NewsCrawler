/*
Copyright (c) 2011, Carlos Tse <copperoxide@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

package jopencc;

import jopencc.util.Dict;
import jopencc.util.Util;

/*
	This is the Zht<->Zhs convertor modified from Jopencc
	Date: 2014/12/15
*/
public class ZhtZhsConvertor {

	//Demo
	public static void main(String[] args){
		//Intialized the convertor
		ZhtZhsConvertor convertor = new ZhtZhsConvertor("./jopencc");

		//Example 1:
		String zht = "這是個測試用的句子，我今天中午吃麵。";
		System.out.println(convertor.convertToZhs(zht));

	}

	private Dict DICT_TO_ZHS, DICT_TO_ZHT;
    public ZhtZhsConvertor(String packagePath){
		DICT_TO_ZHS = new Dict(Dict.ZHT_TO_ZHS);
		DICT_TO_ZHT = new Dict(Dict.ZHS_TO_ZHT);
	    DICT_TO_ZHT.initDict(packagePath);
        DICT_TO_ZHS.initDict(packagePath);
    }
	
	/**
	 * Convert the source to Traditional Chinese
	 * @param src
	 * @return Text in Simplified Chinese
	 */
	public String convertToZht(StringBuffer src){
		if (Util.isMissing(src))
			return src == null? null: src.toString();
		
		try {
			DICT_TO_ZHT.setSrc(src);
			DICT_TO_ZHT.convert();
			return DICT_TO_ZHT.getResult();
			
		} catch (Exception e){
			return src == null? null: src.toString();
		} finally {
			DICT_TO_ZHT.clear();
		}
	}
	
	/**
	 * Convert the source to Traditional Chinese
	 * @param src
	 * @return Text in Simplified Chinese
	 */
	public String convertToZht(String src){
		return Util.isMissing(src)? src: convertToZht(new StringBuffer(src));
	}
	
	/**
	 * Convert the source to Traditional Chinese
	 * @param src
	 * @return Array of texts in Simplified Chinese
	 */
	public String[] convertToZht(String[] src){
		if(src == null){ return null; }
		String[] buf = new String[src.length];
		for(int i = 0; i < src.length; i++){
			buf[i] = convertToZht(src[i]);
		}
		return buf;
	}


	/**
	 * Convert the source to Simplified Chinese
	 * @param src
	 * @return Text in Traditional Chinese
	 */
	public String convertToZhs(StringBuffer src){
		if (Util.isMissing(src))
			return src == null? null: src.toString();
		
		try {
			DICT_TO_ZHS.setSrc(src);
			DICT_TO_ZHS.convert();
			return DICT_TO_ZHS.getResult();
			
		} catch (Exception e){
			return src == null? null: src.toString();
		} finally {
			DICT_TO_ZHS.clear();
		}
	}
	
	/**
	 * Convert the source to Simplified Chinese
	 * @param src
	 * @return Text in Traditional Chinese
	 */
	public String convertToZhs(String src){
		return Util.isMissing(src)? src: convertToZhs(new StringBuffer(src));
	}

	/**
	 * Convert the source to Simplified Chinese
	 * @param src
	 * @return Array of texts in Traditional Chinese
	*/
	public String[] convertToZhs(String[] src){
		if(src == null){ return null; }
		String[] buf = new String[src.length];
		for(int i = 0; i < src.length; i++){
			buf[i] = convertToZhs(src[i]);
		}
		return buf;
	}
}
